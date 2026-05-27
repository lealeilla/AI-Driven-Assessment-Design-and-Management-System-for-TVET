from generator import generate_exam_questions, scale_marks_to_total
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import json, os, re, random, sys

from database import get_db, create_tables, Exam, Question, QuestionBank, Teacher
from schemas import (
    ExamRequest, ExamOut, QuestionOut, TeacherCreate,
    TeacherLogin, TokenResponse, ModuleInfo, QuestionBankItem,
    ExamUpdateRequest, QuestionUpdateRequest, NewQuestionRequest
)
from auth     import hash_password, verify_password, create_token, get_current_teacher

sys.path.append(os.getenv("MODEL_PATH", "../"))

app = FastAPI(
    title       = "TVET Assessment API",
    description = "AI-Driven Assessment Design System for Rwanda TVET",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ═══════════════════════════════════════════════════════════════════════
# GLOBAL STORES
# ═══════════════════════════════════════════════════════════════════════
MANUAL_CONTENT  = {}
MANUAL_DESC_MAP = {}
CLEAN_TERMS     = {}

CODE_RE = re.compile(
    r'(npm\s|node\s|const\s|let\s|var\s|require\(|app\.|router\.|'
    r'mongoose\.|jwt\.|bcrypt\.|async |await |res\.|req\.|'
    r'module\.exports|process\.env|\.env|express\(|Promise|'
    r'\.then\(|\.catch\(|try\s*\{|catch\s*\(|JSON\.|http\.|https\.)'
)

# ═══════════════════════════════════════════════════════════════════════
# EXCLUSION LISTS  — everything that is NOT a real technical topic
# ═══════════════════════════════════════════════════════════════════════
VERB_SET = {
    # Action verbs that slip through as topics
    'analyze','analyse','configure','learning','apply','test','understand',
    'design','implement','deploy','build','explain','create','describe',
    'manage','use','run','get','put','post','delete','identify','define',
    'evaluate','setup','start','stop','check','perform','prepare','write',
    'read','load','save','train','predict','fit','transform','import',
    'export','call','return','handle','generate','execute','initialize',
    'update','remove','add','set','list','show','display','print','log',
    'install','secure','develop','measure','monitor','review','validate',
    'verify','maintain','document','report','plan','select','choose',
    'compare','contrast','classify','summarize','outline','discuss',
    'justify','recommend','assess','critique','argue','judge','defend',
    'formulate','produce','construct','compile','compose','assemble',
    'integrate','combine','organize','arrange','collect','gather',
    'acquire','process','convert','clean','normalize','encode','decode',
    'split','merge','join','filter','sort','search','find','match',
    'replace','insert','append','learn','understand','enable','allow',
    'provide','support','ensure','require','include','contain','store',
    'retrieve','send','receive','connect','disconnect','open','close',
    'read','write','create','delete','update','upload','download',
}

GENERIC_NOUNS = {
    'data','process','system','method','methods','tool','tools',
    'service','services','function','functions','value','values',
    'result','results','output','outputs','type','types','example',
    'examples','feature','features','support','collection','object',
    'objects','class','classes','concept','concepts','step','steps',
    'task','tasks','item','items','part','parts','section','sections',
    'information','approach','approaches','activity','activities',
    'application','applications','apis','browser','coding','it',
    'its','this','that','these','those','they','their','best',
    'way','ways','thing','things','place','places','time','times',
    'number','numbers','set','sets','group','groups','list','lists',
    'file','files','folder','folders','directory','directories',
    'network','networks','server','servers','client','clients',
    'user','users','admin','admins','role','roles','access','request',
    'response','error','errors','message','messages','event','events',
    'name','names','field','fields','column','columns','row','rows',
    'table','tables','record','records','key','keys','index','indices',
}

EXCLUDE_EXACT = VERB_SET | GENERIC_NOUNS

EXCLUDE_PREFIXES = {
    'a ', 'an ', 'the ', 'this ', 'that ', 'these ', 'those ',
    'it ', 'its ', 'their ', 'our ', 'your ', 'my ',
    'o ', 'i ', 'e ',
}

EXCLUDE_PATTERNS = [
    r'^\d',
    r'^\(',
    r'^\)',
    r'^-',
    r'\d+\s*hrs',
    r'^[a-z]\s',              # single lowercase letter + space (OCR)
    r'ltd$',
    r'plant\s+growth',
    r'mietech',
    r'^example\s+',
    r'communicat',
    r'consist',
    r'advantag',
    r'^big\s+data$',
    r'^\d+\.',                # numbered list items
    r'^[ivxlc]+\.',           # roman numerals
]

COMPANY_TERMS = {
    'stu ltd','abc ltd','xyz ltd','musanze','kigali','mietech ltd',
    'mietech','plant growth','rtb','koica','tqum','rwanda tvet',
}


def is_good_term(term: str) -> bool:
    t     = term.strip()
    t_low = t.lower()

    # Length
    if len(t) < 4 or len(t) > 80:
        return False

    # Excluded prefixes
    for prefix in EXCLUDE_PREFIXES:
        if t_low.startswith(prefix):
            return False

    # Exact exclusion
    if t_low in EXCLUDE_EXACT:
        return False

    # Single lowercase word → almost always a verb or generic
    if len(t.split()) == 1 and t[0].islower():
        # Allow well-known lowercase library names
        allowed_lower = {
            'numpy','pandas','flask','keras','pickle','joblib',
            'scikit','sklearn','tensorflow','matplotlib','seaborn',
            'scipy','pytorch','jupyter','vite','npm','pip','git',
        }
        if t_low not in allowed_lower:
            return False

    # Pattern exclusion
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, t_low):
            return False

    # Must contain real letters
    if not re.search(r'[a-zA-Z]{3,}', t):
        return False

    # Must have at least one word ≥ 4 chars
    if not any(len(w) >= 4 for w in t_low.split()):
        return False

    # Company / case-study names
    if any(ex in t_low for ex in COMPANY_TERMS):
        return False

    return True


def is_valid_topic(term: str) -> bool:
    t     = term.strip()
    t_low = t.lower()

    if not is_good_term(t):
        return False

    # Ends with a connector word
    if re.search(r'\s+(and|or|the|a|an|of|in|for|with|to|by|is|are|was)$', t_low):
        return False

    # Ends with punctuation
    if t.endswith(('.', ',', ':', ';')):
        return False

    # Mid-sentence capital = fragment
    if re.search(r'\.\s+[A-Z]', t):
        return False

    # OCR artifact: single letter + space
    if re.match(r'^[a-zA-Z]\s+', t) and len(t) < 10:
        return False

    return True


# ═══════════════════════════════════════════════════════════════════════
# MODULE-SPECIFIC PRIORITY TERMS
# Only real technical nouns — NO verbs, NO generic words
# ═══════════════════════════════════════════════════════════════════════
MODULE_PRIORITY_TERMS = {
    "Vue.JS Framework": [
        'Vue.js','Vue Router','Vuex','Pinia','Vue component',
        'v-for directive','v-if directive','v-bind','v-model','v-on',
        'computed property','lifecycle hook','mounted hook','created hook',
        'props','emit event','slot','ref','reactive data','template syntax',
        'Single File Component','Composition API','Options API',
        'custom directive','event modifier','Netlify deployment',
        'Vite bundler','Game loop','Game canvas','Sprite animation',
        'Phaser framework','component registration','Vue store',
        'route parameter','navigation guard','lazy loading',
    ],
    "Backend Application Development Using Node JS": [
        'Node.js','Express framework','MongoDB','Mongoose ODM',
        'JWT authentication','bcrypt hashing','REST API','RESTful API',
        'Middleware','HTTP Authentication','Authorization header',
        'Data Encryption','Hashing algorithm','npm package manager',
        'dotenv configuration','Mocha test framework','Chai assertion',
        'Jest testing','Supertest','Unit Testing','Integration Testing',
        'Security Testing','Continuous Deployment','Environment Variables',
        'HTTPS protocol','SSL certificate','CORS policy','Rate Limiting',
        'API endpoint','Route handler','Controller function',
        'Database connection','Mongoose Schema','Data Model',
        'JSON Web Token','Salt value','Access Token','Refresh Token',
        'Swagger documentation','Postman testing tool',
        'Node.js Package Manager','Express Router','Mongoose Query',
        'HTTP status code','Request body','Response object',
        'Error handling middleware','Authentication middleware',
    ],
    "Fundamental of Blockchain Application": [
        'Blockchain technology','Smart Contract','Solidity language',
        'Ethereum network','Web3.js library','MetaMask wallet',
        'Remix IDE','Truffle framework','Hardhat framework',
        'ERC-20 token','ERC-721 token','NFT','Decentralized Application',
        'Crypto wallet','Gas fee','Consensus mechanism','Proof of Work',
        'Proof of Stake','Cryptographic hash','Block structure',
        'Distributed ledger','Decentralized network','Smart contract ABI',
        'Contract bytecode','Contract constructor','Solidity mapping',
        'Solidity struct','Solidity event','Function modifier',
        'msg.sender','payable function','IPFS storage',
        'Blockchain architecture','Smart contract security',
        'Token standard','Blockchain transaction','Block explorer',
        'Private key','Public key','Digital signature',
    ],
    "Python Programming Fundamentals": [
        'Python interpreter','pip package manager','Virtual environment',
        'Python Data Types','Python Variables','Arithmetic Operators',
        'Conditional Statements','Looping Statements','Python Function',
        'Lambda function','Recursive function','Python List',
        'Python Tuple','Python Dictionary','Python Set',
        'File Handling','Object-Oriented Programming','Python Class',
        'Python Object','Class Inheritance','Method Overriding',
        'Polymorphism','Encapsulation','Pandas library',
        'NumPy array','Matplotlib chart','Python standard library',
        'datetime module','Python Decorator','Python Generator',
        'Exception handling','Python Module','Python Package',
        'PyPI repository','Python syntax','Code indentation',
        'virtualenv tool','requirements.txt','Python script',
        'Frozen Set','ChainMap','defaultdict','OrderedDict',
    ],
    "Machine Learning Application": [
        'Machine Learning','Supervised Learning','Unsupervised Learning',
        'Reinforcement Learning','Training dataset','Test dataset',
        'Validation dataset','Input feature','Target label',
        'Prediction model','ML Algorithm','Model Accuracy',
        'Precision score','Recall score','F1 score',
        'Overfitting problem','Underfitting problem','Cross-validation',
        'Bias-Variance tradeoff','Linear Regression','Logistic Regression',
        'Decision Tree algorithm','Random Forest','Support Vector Machine',
        'K-Means clustering','K-Nearest Neighbors','Neural Network',
        'Deep Learning','scikit-learn library','TensorFlow framework',
        'Keras API','Pandas DataFrame','NumPy array','Matplotlib plot',
        'Data preprocessing','Feature normalization','Data standardization',
        'Categorical encoding','Confusion matrix','Gradient descent',
        'Loss function','Training epoch','Batch size','Learning rate',
        'Activation function','Flask API','FastAPI framework',
        'Model deployment','Pickle serialization','Joblib library',
        'Data collection','Data cleaning','Feature engineering',
        'Model training','Model evaluation','Hyperparameter tuning',
        'Data Gathering','Data wrangling','Data preparation',
        'Machine learning life cycle','Model integration',
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# TERM EXTRACTION — uses ONLY priority terms + definition subjects
# ═══════════════════════════════════════════════════════════════════════
def extract_terms_from_definitions(outcome_data: dict, priority_terms: list) -> list:
    """
    Extract real technical terms for question generation.
    Sources (in order of reliability):
      1. Priority whitelist terms present in this outcome's text
      2. Definition subjects: "X is a/an/the ..."
    Never uses raw NLP key_terms — too many verbs.
    """
    terms    = []
    raw_text = " ".join(outcome_data.get("raw_lines", []))
    raw_low  = raw_text.lower()

    # 1. Priority terms that actually appear in this outcome
    for pt in priority_terms:
        if pt.lower() in raw_low and pt not in terms:
            terms.append(pt)

    # 2. Definition subjects only
    for defn in outcome_data.get("definitions", []):
        m = re.match(
            r'^([A-Za-z][A-Za-z0-9\s\.\(\)/\-]{2,45}?)\s+'
            r'(is a|is an|is the|refers to|means |defined as|stands for)\b',
            defn
        )
        if m:
            term      = m.group(1).strip()
            first_word = term.split()[0].lower()
            # Reject if first word is a verb or generic
            if (is_good_term(term) and
                    term not in terms and
                    first_word not in EXCLUDE_EXACT and
                    # Must start uppercase or be an acronym
                    (term[0].isupper() or term.upper() == term)):
                terms.append(term)

    # Remove any that slipped through validation
    terms = [t for t in terms if is_valid_topic(t)]

    return terms[:40]


# ═══════════════════════════════════════════════════════════════════════
# MANUAL LOADER
# ═══════════════════════════════════════════════════════════════════════
def load_manual(json_path: str, desc_path: str, module_key: str):
    if not os.path.exists(json_path):
        print(f"  [SKIP] Not found: {json_path}")
        return

    with open(json_path,  "r") as f: content  = json.load(f)
    with open(desc_path,  "r") as f: desc_map = json.load(f)

    MANUAL_CONTENT[module_key]  = content
    MANUAL_DESC_MAP[module_key] = desc_map

    # Use module-specific priority list — NO fallback to generic PRIORITY_TERMS
    priority = MODULE_PRIORITY_TERMS.get(module_key, [])

    for outcome, data in content.items():
        key   = f"{module_key}::{outcome}"
        terms = extract_terms_from_definitions(data, priority)
        CLEAN_TERMS[key] = terms

    print(f"Manual loaded: {module_key} — {len(content)} outcomes")
    for outcome in content:
        key   = f"{module_key}::{outcome}"
        terms = CLEAN_TERMS[key]
        print(f"  [{outcome[:45]}] → {len(terms)} terms: {terms[:6]}")


# ═══════════════════════════════════════════════════════════════════════
# MANUAL REGISTRY
# ═══════════════════════════════════════════════════════════════════════
MANUAL_REGISTRY = {
    "Vue.JS Framework": {
        "json"    : "manual_vue.json",
        "desc_map": "desc_map_vue.json",
        "outcomes": [
            "Set Up Environment",
            "Apply Vue Framework",
            "Plan game",
            "Develop Game",
        ],
        "program" : "SOFTWARE DEVELOPMENT",
        "level"   : 3,
    },
    "Backend Application Development Using Node JS": {
        "json"    : "manual_node.json",
        "desc_map": "desc_map_node.json",
        "outcomes": [
            "Develop RESTFUL APIs with Node JS",
            "Secure Backend Application",
            "Test Backend Application",
            "Manage Backend Application",
        ],
        "program" : "SOFTWARE DEVELOPMENT",
        "level"   : 4,
    },
    "Fundamental of Blockchain Application": {
        "json"    : "manual_blockchain.json",
        "desc_map": "desc_map_blockchain.json",
        "outcomes": [
            "Design Blockchain System Architecture",
            "Apply Solidity Basics",
            "Develop Smart Contracts System",
            "Apply Frontend Integration",
        ],
        "program" : "SOFTWARE DEVELOPMENT",
        "level"   : 5,
    },
    "Python Programming Fundamentals": {
        "json"    : "manual_python.json",
        "desc_map": "desc_map_python.json",
        "outcomes": [
            "Prepare python environment",
            "Write basic python program",
            "Apply object-driven in python",
        ],
        "program" : "SOFTWARE DEVELOPMENT",
        "level"   : 5,
    },
    "Machine Learning Application": {
        "json"    : "manual_ml.json",
        "desc_map": "desc_map_ml.json",
        "outcomes": [
            "Apply Data Pre-processing",
            "Develop Machine Learning Model",
            "Perform Model Deployment",
        ],
        "program" : "SOFTWARE DEVELOPMENT",
        "level"   : 5,
    },
}


# ═══════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════
@app.on_event("startup")
def startup():
    create_tables()
    for module_key, info in MANUAL_REGISTRY.items():
        load_manual(info["json"], info["desc_map"], module_key)
    print("\nTVET Assessment API started!")


@app.get("/")
def root():
    return {"message": "TVET Assessment API", "status": "running"}


# ═══════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════
@app.post("/auth/register", response_model=TokenResponse)
def register(data: TeacherCreate, db: Session = Depends(get_db)):
    if db.query(Teacher).filter(Teacher.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    teacher = Teacher(
        name     = data.name,
        email    = data.email,
        password = hash_password(data.password),
        school   = data.school,
    )
    db.add(teacher); db.commit(); db.refresh(teacher)
    token = create_token({"sub": teacher.email})
    return {"access_token": token, "teacher_name": teacher.name}


@app.post("/auth/login", response_model=TokenResponse)
def login(data: TeacherLogin, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == data.email).first()
    if not teacher or not verify_password(data.password, teacher.password):
        raise HTTPException(401, "Invalid email or password")
    token = create_token({"sub": teacher.email})
    return {"access_token": token, "teacher_name": teacher.name}


# ═══════════════════════════════════════════════════════════════════════
# MODULES
# ═══════════════════════════════════════════════════════════════════════
@app.get("/modules", response_model=list[ModuleInfo])
def get_modules():
    return [
        {
            "program" : info["program"],
            "level"   : info["level"],
            "module"  : module_key,
            "outcomes": ["all"] + info["outcomes"],
        }
        for module_key, info in MANUAL_REGISTRY.items()
    ]


# ═══════════════════════════════════════════════════════════════════════
# GENERATE EXAM
# ═══════════════════════════════════════════════════════════════════════
@app.post("/exams/generate", response_model=ExamOut)
def generate_exam(
    request : ExamRequest,
    db      : Session = Depends(get_db),
    teacher : Teacher = Depends(get_current_teacher),
):
    # ── Find module ────────────────────────────────────────────────
    module_key = next(
        (k for k in MANUAL_REGISTRY if request.module.lower() in k.lower()),
        None
    )
    if not module_key:
        raise HTTPException(400,
            f"Module not found: {request.module}. "
            f"Available: {list(MANUAL_REGISTRY.keys())}")

    content  = MANUAL_CONTENT.get(module_key)
    desc_map = MANUAL_DESC_MAP.get(module_key)
    info     = MANUAL_REGISTRY[module_key]

    if not content:
        raise HTTPException(500, f"Manual not loaded for: {module_key}")

    all_outcomes = info["outcomes"]

    # ── Formative vs Summative ─────────────────────────────────────
    if request.learning_outcome.lower() == "all":
        assessment_type   = "Summative"
        selected_outcomes = all_outcomes
    else:
        matched = [o for o in all_outcomes
                   if request.learning_outcome.lower() in o.lower()]
        if not matched:
            raise HTTPException(400,
                f"Outcome '{request.learning_outcome}' not found. "
                f"Available: {all_outcomes}")
        assessment_type   = "Formative"
        selected_outcomes = matched

    n = request.num_questions

    # ── Question type pool ─────────────────────────────────────────
    type_pool = (
        ['mcq']        * max(1, int(n * 0.35)) +
        ['true_false'] * max(1, int(n * 0.20)) +
        ['matching']   * max(1, int(n * 0.10)) +
        ['open']       * max(1, int(n * 0.35))
    )
    while len(type_pool) < n: type_pool.append('open')
    type_pool = type_pool[:n]
    random.shuffle(type_pool)

    # ── Balanced Bloom distribution ────────────────────────────────
    bloom_map = {
        'remember'  : max(1, int(n * 0.15)),
        'understand': max(1, int(n * 0.20)),
        'apply'     : max(1, int(n * 0.30)),
        'analyze'   : max(1, int(n * 0.20)),
        'evaluate'  : max(1, int(n * 0.10)),
        'create'    : max(1, int(n * 0.05)),
    }
    bloom_list = []
    for level, count in bloom_map.items():
        bloom_list.extend([level] * count)
    while len(bloom_list) < n: bloom_list.append('apply')
    bloom_list = random.sample(bloom_list[:n], len(bloom_list[:n]))

    # ── Distribute questions across outcomes ───────────────────────
    n_out     = len(selected_outcomes)
    base      = n // n_out
    remainder = n  % n_out
    q_per_out = {
        lo: base + (1 if i < remainder else 0)
        for i, lo in enumerate(selected_outcomes)
    }

    # ── Module-wide distractor pool (valid terms only) ─────────────
    all_module_terms = []
    for o in all_outcomes:
        key = f"{module_key}::{o}"
        all_module_terms.extend(CLEAN_TERMS.get(key, []))
    all_module_terms = list(dict.fromkeys(
        [t for t in all_module_terms if is_valid_topic(t)]
    ))
    verb_map = {
        'develop' :'developing', 'secure'  :'securing',
        'test'    :'testing',    'manage'  :'managing',
        'prepare' :'preparing',  'write'   :'writing',
        'apply'   :'applying',   'implement':'implementing',
        'perform' :'performing', 'design'  :'designing',
        'plan'    :'planning',   'set up'  :'setting up',
    }

    def fmt_phrase(outcome: str) -> str:
        o_low = outcome.lower()
        for verb, gerund in verb_map.items():
            if o_low.startswith(verb + ' ') or o_low == verb:
                rest = outcome[len(verb):].strip()
                return gerund + (' ' + rest if rest else '')
        return outcome
   
    all_questions = []
    q_number      = 1

    for outcome, count in q_per_out.items():
        phrase       = fmt_phrase(outcome)
        key          = f"{module_key}::{outcome}"
        outcome_data = content.get(outcome, {})

        # Get valid terms for this outcome
        module_priority = MODULE_PRIORITY_TERMS.get(module_key, [])
        key_terms       = CLEAN_TERMS.get(key, [])
        priority_valid  = [t for t in key_terms
                           if t in module_priority and is_valid_topic(t)]
        other_valid     = [t for t in key_terms
                           if t not in module_priority and is_valid_topic(t)]
        valid_terms     = priority_valid + other_valid

        if not valid_terms:
            raw_text    = " ".join(str(l) for l in outcome_data.get("raw_lines", []))
            valid_terms = [t for t in module_priority
                           if t.lower() in raw_text.lower()]
        if not valid_terms:
            valid_terms = module_priority[:10] if module_priority else [outcome]

        print(f"  [{outcome}] {count} questions | {len(valid_terms)} terms: {valid_terms[:5]}")

        qs = generate_exam_questions(
            outcome      = outcome,
            outcome_data = outcome_data,
            desc_map     = desc_map,
            valid_terms  = valid_terms,
            all_terms    = all_module_terms,
            count        = count,
            module       = module_key,
            phrase       = phrase,
            bloom_map    = bloom_map,
        )

        for q in qs:
            q["number"] = q_number
            q_number   += 1

        all_questions.extend(qs)

    all_questions = scale_marks_to_total(all_questions, request.total_marks)
    df_exam       = pd.DataFrame(all_questions)

    # ── Save exam to DB ────────────────────────────────────────────
    exam_db = Exam(
        teacher_id      = teacher.id,
        program         = request.program,
        level           = request.level,
        module          = request.module,
        learning_outcome= request.learning_outcome,
        assessment_type = assessment_type,
        num_questions   = request.num_questions,
        total_marks     = request.total_marks,
        exam_date       = request.exam_date,
        time_allowed    = request.time_allowed,
    )
    db.add(exam_db); db.commit(); db.refresh(exam_db)

    questions_out = []
    for _, row in df_exam.iterrows():
        opts = row["options"] if isinstance(row["options"], list) else []
        q = Question(
            exam_id         = exam_db.id,
            number          = int(row["number"]),
            learning_outcome= str(row["learning_outcome"]),
            bloom_level     = str(row["bloom_level"]),
            question_type   = str(row["question_type"]),
            question        = str(row["question"]),
            options         = opts,
            correct_answer  = str(row.get("correct_answer", "")),
            marks           = int(row["marks"]),
            topic           = str(row.get("topic", "")),
        )
        db.add(q)

        bank_q = QuestionBank(
            program         = request.program,
            level           = request.level,
            module          = request.module,
            learning_outcome= str(row["learning_outcome"]),
            bloom_level     = str(row["bloom_level"]),
            question_type   = str(row["question_type"]),
            question        = str(row["question"]),
            options         = opts,
            correct_answer  = str(row.get("correct_answer", "")),
            marks           = int(row["marks"]),
            topic           = str(row.get("topic", "")),
        )
        db.add(bank_q)

        questions_out.append(QuestionOut(
            number          = int(row["number"]),
            learning_outcome= str(row["learning_outcome"]),
            bloom_level     = str(row["bloom_level"]),
            question_type   = str(row["question_type"]),
            question        = str(row["question"]),
            options         = opts,
            correct_answer  = str(row.get("correct_answer", "")),
            marks           = int(row["marks"]),
            topic           = str(row.get("topic", "")),
        ))

    db.commit()

    return ExamOut(
        exam_id         = exam_db.id,
        program         = request.program,
        level           = request.level,
        module          = request.module,
        assessment_type = assessment_type,
        total_marks     = request.total_marks,
        num_questions   = request.num_questions,
        questions       = questions_out,
    )


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD EXAM PDF
# ═══════════════════════════════════════════════════════════════════════
@app.get("/exams/{exam_id}/pdf")
def download_exam_pdf(
    exam_id: int,
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    exam      = db.query(Exam).filter(Exam.id == exam_id).first()
    questions = db.query(Question).filter(Question.exam_id == exam_id).all()
    if not exam or not questions:
        raise HTTPException(404, "Exam not found")

    rows = [{
        "number"          : q.number,
        "learning_outcome": q.learning_outcome,
        "bloom_level"     : q.bloom_level,
        "question_type"   : q.question_type,
        "question"        : q.question,
        "options"         : q.options,
        "marks"           : q.marks,
        "correct_answer"  : q.correct_answer,
        "topic"           : q.topic,
    } for q in questions]

    df       = pd.DataFrame(rows)
    csv_path = f"temp_exam_{exam_id}.csv"
    pdf_path = f"exam_{exam_id}.pdf"
    df.to_csv(csv_path, index=False)

    from pdf_builder import build_exam_pdf
    build_exam_pdf(
        exam_csv        = csv_path,
        output_path     = pdf_path,
        school_name     =teacher.school,
        program         = exam.program,
        module          = exam.module,
        level           = str(exam.level),
        exam_date       = exam.exam_date,
        time_allowed    = exam.time_allowed,
        total_marks     = exam.total_marks,
        assessment_type = exam.assessment_type,
        outcomes        = [],
    )
    os.remove(csv_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"exam_{exam.module}_{exam_id}.pdf"
    )

@app.post("/exams/{exam_id}/questions")
def add_question(
    exam_id: int,
    request: NewQuestionRequest,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == teacher.id).first()
    if not exam:
        raise HTTPException(404, "Exam not found")
    
    # Get the highest question number
    max_num = db.query(Question).filter(Question.exam_id == exam_id).order_by(Question.number.desc()).first()
    new_number = max_num.number + 1 if max_num else 1
    
    new_q = Question(
        exam_id=exam_id,
        number=new_number,
        learning_outcome=request.learning_outcome,
        bloom_level=request.bloom_level,
        question_type=request.question_type,
        question=request.question,
        options=request.options,
        correct_answer=request.correct_answer,
        marks=request.marks,
        topic=request.topic
    )
    db.add(new_q)
    
    # Update exam totals
    exam.num_questions += 1
    exam.total_marks += request.marks
    
    db.commit()
    db.refresh(new_q)
    return {"message": "Question added successfully", "question_id": new_q.id}

# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD MARKING GUIDE
# ═══════════════════════════════════════════════════════════════════════
@app.get("/exams/{exam_id}/marking-guide")
def download_marking_guide(
    exam_id: int,
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    exam      = db.query(Exam).filter(Exam.id == exam_id).first()
    questions = db.query(Question).filter(Question.exam_id == exam_id).all()
    if not exam or not questions:
        raise HTTPException(404, "Exam not found")

    rows = [{
        "number"          : q.number,
        "question_type"   : q.question_type,
        "question"        : q.question,
        "marks"           : q.marks,
        "correct_answer"  : q.correct_answer,
        "bloom_level"     : q.bloom_level,
        "learning_outcome": q.learning_outcome,
        "model_answer"    : q.correct_answer,
        "explanation"     : f"Bloom level: {q.bloom_level}",
        "marks_guide"     : f"Award {q.marks} marks for correct and complete answer.",
    } for q in questions]

    df       = pd.DataFrame(rows)
    pdf_path = f"marking_guide_{exam_id}.pdf"

    from pdf_builder import build_marking_guide_pdf
    build_marking_guide_pdf(
        df_answers      = df,
        output_path     = pdf_path,
        module          = exam.module,
        program         = exam.program,
        level           = str(exam.level),
        total_marks     = exam.total_marks,
        exam_date       = exam.exam_date,
        assessment_type = exam.assessment_type,
    )
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"marking_guide_{exam_id}.pdf"
    )


# ═══════════════════════════════════════════════════════════════════════
# QUESTION BANK
# ═══════════════════════════════════════════════════════════════════════
@app.get("/question-bank", response_model=list[QuestionBankItem])
def get_question_bank(
    module : str  = None,
    level  : int  = None,
    qtype  : str  = None,
    bloom  : str  = None,
    skip   : int  = 0,
    limit  : int  = 50,
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    query = db.query(QuestionBank)
    if module: query = query.filter(QuestionBank.module.ilike(f"%{module}%"))
    if level : query = query.filter(QuestionBank.level == level)
    if qtype : query = query.filter(QuestionBank.question_type == qtype)
    if bloom : query = query.filter(QuestionBank.bloom_level == bloom)
    return query.offset(skip).limit(limit).all()


@app.get("/exams", response_model=list[dict])
def get_my_exams(
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    exams = (db.query(Exam)
               .filter(Exam.teacher_id == teacher.id)
               .order_by(Exam.created_at.desc())
               .all())
    return [{
        "id"             : e.id,
        "module"         : e.module,
        "level"          : e.level,
        "assessment_type": e.assessment_type,
        "num_questions"  : e.num_questions,
        "total_marks"    : e.total_marks,
        "exam_date"      : e.exam_date,
        "created_at"     : str(e.created_at),
    } for e in exams]

@app.get("/dashboard/stats")
def get_dashboard_stats(teacher: Teacher = Depends(get_current_teacher), db: Session = Depends(get_db)):
    total_exams = db.query(Exam).filter(Exam.teacher_id == teacher.id).count()
    total_questions = db.query(Question).join(Exam).filter(Exam.teacher_id == teacher.id).count()
    modules = db.query(Exam.module).filter(Exam.teacher_id == teacher.id).distinct().all()
    recent_exams = db.query(Exam).filter(Exam.teacher_id == teacher.id).order_by(Exam.created_at.desc()).limit(5).all()
    return {
        "total_exams": total_exams,
        "total_questions": total_questions,
        "total_modules": len(modules),
        "recent_exams": [{"id": e.id, "module": e.module, "created_at": str(e.created_at)} for e in recent_exams]
    }

# ── UPDATE EXAM ──────────────────────────────────────────────────────────
@app.put("/exams/{exam_id}")
def update_exam(
    exam_id: int,
    request: ExamUpdateRequest,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == teacher.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    for key, value in request.dict(exclude_unset=True).items():
        setattr(exam, key, value)
    
    db.commit()
    db.refresh(exam)
    return {"message": "Exam updated", "exam_id": exam.id}


# ── DELETE EXAM ──────────────────────────────────────────────────────────
@app.delete("/exams/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.teacher_id == teacher.id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Delete all questions associated with this exam
    db.query(Question).filter(Question.exam_id == exam_id).delete()
    
    # Delete the exam
    db.delete(exam)
    db.commit()
    return {"message": "Exam deleted", "exam_id": exam.id}