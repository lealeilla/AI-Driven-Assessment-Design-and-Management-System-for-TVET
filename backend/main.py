from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import json, os, sys, shutil

from database import get_db, create_tables, Exam, Question, QuestionBank, Teacher
from schemas  import (ExamRequest, ExamOut, QuestionOut, TeacherCreate,
                      TeacherLogin, TokenResponse, ModuleInfo, QuestionBankItem)
from auth     import hash_password, verify_password, create_token, get_current_teacher

# Add your AI model path
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

# ── Startup ───────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    create_tables()
    # Load all training manuals
    for module_key, info in MANUAL_REGISTRY.items():
        load_manual(info["json"], info["desc_map"], module_key)
    print("TVET Assessment API started!")

# ── Health check ──────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "TVET Assessment API", "status": "running"}

# ── AUTH ROUTES ───────────────────────────────────────────────────────
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
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    token = create_token({"sub": teacher.email})
    return {"access_token": token, "teacher_name": teacher.name}


@app.post("/auth/login", response_model=TokenResponse)
def login(data: TeacherLogin, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == data.email).first()
    if not teacher or not verify_password(data.password, teacher.password):
        raise HTTPException(401, "Invalid email or password")

    token = create_token({"sub": teacher.email})
    return {"access_token": token, "teacher_name": teacher.name}


# ── ADD at top of main.py after imports ───────────────────────────────
import json, pickle, re, random

# Load manual content on startup
MANUAL_CONTENT  = {}
MANUAL_DESC_MAP = {}
CLEAN_TERMS     = {}

PRIORITY_TERMS = [
    'Node.js', 'Express', 'MongoDB', 'Mongoose', 'JWT', 'bcrypt',
    'REST API', 'RESTful API', 'Middleware', 'Authentication',
    'Authorization', 'Encryption', 'Hashing', 'npm', 'dotenv',
    'Mocha', 'Chai', 'Jest', 'Supertest', 'Unit Testing',
    'Security Testing', 'Usability Testing', 'Deployment',
    'Environment Variables', 'HTTPS', 'SSL', 'CORS', 'Rate Limiting',
    'API endpoint', 'HTTP methods', 'GET', 'POST', 'PUT', 'DELETE',
    'Request body', 'Response', 'Route handler', 'Controller',
    'Database connection', 'Schema', 'Model', 'JSON Web Token',
    'Salt', 'Hash', 'Token', 'Continuous deployment', 'Swagger', 'Postman',

     # ── Node JS (Level 4) ──────────────────────────────────────────────
    'Node.js', 'Express', 'MongoDB', 'Mongoose', 'JWT', 'bcrypt',
    'REST API', 'RESTful API', 'Middleware', 'Authentication',
    'Authorization', 'Encryption', 'Hashing', 'npm', 'dotenv',
    'Mocha', 'Chai', 'Jest', 'Supertest', 'Unit Testing',
    'Security Testing', 'Usability Testing', 'Deployment',
    'Environment Variables', 'HTTPS', 'SSL', 'CORS', 'Rate Limiting',
    'API endpoint', 'HTTP methods', 'GET', 'POST', 'PUT', 'DELETE',
    'Request body', 'Response', 'Route handler', 'Controller',
    'Database connection', 'Schema', 'Model', 'JSON Web Token',
    'Salt', 'Hash', 'Token', 'Continuous deployment', 'Swagger', 'Postman',

    # ── Vue.JS (Level 3) ───────────────────────────────────────────────
    'Vue.js', 'Vue component', 'Vue Router', 'Vuex', 'Pinia',
    'v-for', 'v-if', 'v-bind', 'v-model', 'v-on',
    'computed property', 'lifecycle hook', 'mounted', 'created',
    'props', 'emit', 'slot', 'ref', 'reactive', 'template',
    'Component', 'Single File Component', 'Composition API',
    'Options API', 'directive', 'event modifier', 'Netlify',
    'npm install', 'vite', 'package.json', 'Game loop',
    'Game mechanics', 'Canvas', 'Sprite', 'Phaser',

    # ── Blockchain (Level 5) ───────────────────────────────────────────
    'Blockchain', 'Smart Contract', 'Solidity', 'Ethereum',
    'Web3.js', 'MetaMask', 'Remix IDE', 'Truffle', 'Hardhat',
    'Token', 'NFT', 'DApp', 'Wallet', 'Gas fee',
    'Consensus mechanism', 'Proof of Work', 'Proof of Stake',
    'Hash function', 'Block', 'Node', 'Ledger', 'Decentralized',
    'ERC-20', 'ERC-721', 'ABI', 'Bytecode', 'Deployment',
    'Constructor', 'Mapping', 'Struct', 'Event', 'Modifier',
    'require statement', 'msg.sender', 'payable', 'IPFS',

    # ── Python (Level 5) ───────────────────────────────────────────────
    'Python', 'pip', 'virtual environment', 'Data Types',
    'Variables', 'Operators', 'Conditional Statements',
    'Looping Statements', 'Function', 'Lambda', 'Recursion',
    'List', 'Tuple', 'Dictionary', 'Set', 'File Handling',
    'OOP', 'Class', 'Object', 'Inheritance', 'Polymorphism',
    'Encapsulation', 'Pandas', 'NumPy', 'Matplotlib',
    'Python standard library', 'Datetime', 'Decorator',
    'Generator', 'Exception handling', 'Module', 'Package',

    # ── Machine Learning (Level 5) ─────────────────────────────────────
    'Machine Learning', 'Supervised Learning', 'Unsupervised Learning',
    'Dataset', 'Training data', 'Test data', 'Validation data',
    'Feature', 'Label', 'Model', 'Algorithm', 'Accuracy',
    'Overfitting', 'Underfitting', 'Cross-validation',
    'Linear Regression', 'Logistic Regression', 'Decision Tree',
    'Random Forest', 'SVM', 'K-Means', 'Neural Network',
    'scikit-learn', 'TensorFlow', 'Keras', 'Pandas', 'NumPy',
    'Data preprocessing', 'Normalization', 'Encoding',
    'Confusion matrix', 'Precision', 'Recall', 'F1 score',
    'Gradient descent', 'Loss function', 'Epoch', 'Batch size',
    'Flask', 'Model deployment', 'Pickle', 'Joblib', 'API',
]

EXCLUDE_STARTS = {
    'a ', 'an ', 'the ', 'this ', 'that ', 'these ', 'those ',
    'it ', 'its ', 'their ', 'our ', 'your ', 'my ',
}
EXCLUDE_EXACT = {
    'apis','application','applications','best','browser','angular',
    'activity','attention','attitudes','approach','coding','information',
    'data','process','system','method','methods','tool','tools',
    'service','services','function','functions','value','values',
    'result','results','output','outputs','type','types','example',
    'examples','feature','features','support','collection','object',
    'objects','class','classes',
}
EXCLUDE_CONTAINS = [
    r'^\d', r'^\(', r'^\)', r'^-', r'\d+\s*hrs',
    r'which$', r'^what', r'^how', r'^when', r'^where', r'^why',
]
EXCLUDE_TERMS = {
    'stu ltd','abc ltd','xyz ltd','musanze','kigali',
    'rtb','koica','tqum','rwanda tvet',
}

CODE_RE = re.compile(
    r'(npm\s|node\s|const\s|let\s|var\s|require\(|app\.|router\.|'
    r'mongoose\.|jwt\.|bcrypt\.|async |await |res\.|req\.|'
    r'module\.exports|process\.env|\.env|express\(|Promise|'
    r'\.then\(|\.catch\(|try\s*\{|catch\s*\(|JSON\.|http\.|https\.)'
)


def is_good_term(term):
    t     = term.strip()
    t_low = t.lower()
    if len(t) < 3 or len(t) > 60: return False
    for start in EXCLUDE_STARTS:
        if t_low.startswith(start): return False
    if t_low in EXCLUDE_EXACT: return False
    for pat in EXCLUDE_CONTAINS:
        if re.search(pat, t_low): return False
    if not re.search(r'[a-zA-Z]{3,}', t): return False
    return True


def extract_terms_from_definitions(outcome_data, priority_terms):
    terms    = []
    raw_text = " ".join(outcome_data.get("raw_lines", []))
    raw_low  = raw_text.lower()
    for pt in priority_terms:
        if pt.lower() in raw_low:
            terms.append(pt)
    for defn in outcome_data.get("definitions", []):
        m = re.match(
            r'^([A-Za-z][A-Za-z0-9\s\.\(\)/\-]{2,40}?)\s+'
            r'(is a|is an|is the|refers to|means |defined as|stands for)\b',
            defn
        )
        if m:
            term = m.group(1).strip()
            if is_good_term(term) and term not in terms:
                terms.append(term)
    for t in outcome_data.get("key_terms", []):
        if is_good_term(t) and t not in terms:
            terms.append(t)
    return terms[:40]


def load_manual(json_path: str, desc_path: str, module_key: str):
    """Load a training manual JSON into global stores."""
    if not os.path.exists(json_path):
        print(f"Manual not found: {json_path}")
        return
    with open(json_path,  "r") as f: content  = json.load(f)
    with open(desc_path,  "r") as f: desc_map = json.load(f)

    MANUAL_CONTENT[module_key]  = content
    MANUAL_DESC_MAP[module_key] = desc_map

    for outcome, data in content.items():
        key = f"{module_key}::{outcome}"
        CLEAN_TERMS[key] = extract_terms_from_definitions(data, PRIORITY_TERMS)

    print(f"Manual loaded: {module_key} — {len(content)} outcomes")


# ── MANUAL REGISTRY — add more manuals here as you process them ────────
MANUAL_REGISTRY = {
    # ── LEVEL 3 ───────────────────────────────────────────────────────
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

    # ── LEVEL 4 ───────────────────────────────────────────────────────
    "Backend Application Development Using Node JS": {
        "json"    : "manual_node.json",
        "desc_map": "desc_map_node.json",
        "outcomes": [
            "Develop RESTFUL APIs with Node JS",
            "Secure Backend Application",
            "Test Backend Application",
            "Manage Backend Application",
        ],
        "program": "SOFTWARE DEVELOPMENT",
        "level"  : 4,
    },

    # ── LEVEL 5 ───────────────────────────────────────────────────────
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
    # Add more modules here when you process their manuals:
    # "Game Development In Vue Framework": {
    #     "json": "../manual_vue.json", ...
    # },
}

# ── MODULES ROUTE ─────────────────────────────────────────────────────
@app.get("/modules", response_model=list[ModuleInfo])
def get_modules():
    result = []
    for module_key, info in MANUAL_REGISTRY.items():
        result.append({
            "program" : info["program"],
            "level"   : info["level"],
            "module"  : module_key,
            "outcomes": ["all"] + info["outcomes"],
        })
    return result


# ── GENERATE EXAM ─────────────────────────────────────────────────────
@app.post("/exams/generate", response_model=ExamOut)
def generate_exam(
    request : ExamRequest,
    db      : Session = Depends(get_db),
    teacher : Teacher = Depends(get_current_teacher),
):
    # ── Find module in registry ────────────────────────────────────
    module_key = next(
        (k for k in MANUAL_REGISTRY if request.module.lower() in k.lower()),
        None
    )
    if not module_key:
        raise HTTPException(400, f"Module not found: {request.module}. "
                                  f"Available: {list(MANUAL_REGISTRY.keys())}")

    content  = MANUAL_CONTENT.get(module_key)
    desc_map = MANUAL_DESC_MAP.get(module_key)
    info     = MANUAL_REGISTRY[module_key]

    if not content:
        raise HTTPException(500, f"Manual not loaded for: {module_key}")

    all_outcomes = info["outcomes"]

    # ── Select outcomes based on formative/summative ───────────────
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

    # ── Build question pool ────────────────────────────────────────
    n              = request.num_questions
    type_pool      = (
        ['mcq']        * int(n * 0.35) +
        ['true_false'] * int(n * 0.20) +
        ['matching']   * int(n * 0.10) +
        ['open']       * int(n * 0.35)
    )
    while len(type_pool) < n: type_pool.append('open')
    type_pool = type_pool[:n]
    random.shuffle(type_pool)

    bloom_map  = {
        'create':max(1,int(n*0.05)),'evaluate':max(1,int(n*0.10)),
        'analyze':max(1,int(n*0.20)),'apply':max(1,int(n*0.30)),
        'understand':max(1,int(n*0.20)),'remember':max(1,int(n*0.15)),
    }
    bloom_list = []
    for level, count in bloom_map.items():
        bloom_list.extend([level]*count)
    while len(bloom_list) < n: bloom_list.append('apply')
    bloom_list = random.sample(bloom_list[:n], len(bloom_list[:n]))

    # Question distribution across outcomes
    n_out     = len(selected_outcomes)
    base      = n // n_out
    remainder = n  % n_out
    q_per_out = {
        lo: base + (1 if i < remainder else 0)
        for i, lo in enumerate(selected_outcomes)
    }

    # ── Generate questions from manual ─────────────────────────────
    all_questions = []
    q_number      = 1
    bloom_idx     = 0
    type_idx      = 0

    verb_map = {
        'develop':'developing','secure':'securing','test':'testing',
        'manage':'managing','prepare':'preparing','write':'writing',
        'apply':'applying','implement':'implementing',
    }

    def fmt_phrase(outcome):
        o_low = outcome.lower()
        for verb, gerund in verb_map.items():
            if o_low.startswith(verb + ' ') or o_low == verb:
                return gerund + outcome[len(verb):]
        return outcome

    all_module_terms = []
    for o in selected_outcomes:
        key = f"{module_key}::{o}"
        all_module_terms.extend(CLEAN_TERMS.get(key, []))
    all_module_terms = list(dict.fromkeys(all_module_terms))

    for outcome, count in q_per_out.items():
        phrase        = fmt_phrase(outcome)
        outcome_data  = content.get(outcome, {})
        sections      = list(outcome_data.get("indicative_sections", {}).keys())
        key           = f"{module_key}::{outcome}"
        key_terms     = CLEAN_TERMS.get(key, [outcome])

        for i in range(count):
            bloom   = bloom_list[bloom_idx % len(bloom_list)]
            qtype   = type_pool[type_idx % len(type_pool)]
            topic   = key_terms[i % len(key_terms)]
            section = sections[i % len(sections)] if sections else "General"
            bloom_idx += 1
            type_idx  += 1

            options        = []
            correct_answer = ""

            # ── MCQ ───────────────────────────────────────────────
            if qtype == 'mcq':
                q_templates = {
                    'remember'  : f"Which of the following correctly defines {topic}?",
                    'understand': f"What is the main purpose of {topic} when {phrase}?",
                    'apply'     : f"How would you correctly apply {topic} when {phrase}?",
                    'analyze'   : f"What is the key difference when using {topic} for {phrase}?",
                    'evaluate'  : f"Which approach to {topic} is most effective when {phrase}?",
                    'create'    : f"Which design using {topic} would best support {phrase}?",
                }
                question       = q_templates.get(bloom, q_templates['understand'])
                distractors    = [t for t in all_module_terms if t.lower() != topic.lower()]
                chosen         = random.sample(distractors, min(3, len(distractors)))
                opts_list      = [topic] + chosen
                random.shuffle(opts_list)
                letters        = ['A','B','C','D']
                options        = [f"{letters[j]}. {opts_list[j]}" for j in range(len(opts_list))]
                correct_answer = letters[opts_list.index(topic)]

            # ── True/False ────────────────────────────────────────
            elif qtype == 'true_false':
                tf_templates = [
                    f"{topic} is essential when {phrase}.",
                    f"Understanding {topic} is required before {phrase}.",
                    f"It is possible to complete {phrase} without using {topic}.",
                    f"{topic} directly affects the security of {phrase}.",
                ]
                question       = random.choice(tf_templates)
                options        = ["A. True", "B. False"]
                correct_answer = "False" if "without" in question else "True"

            # ── Matching ──────────────────────────────────────────
            elif qtype == 'matching':
                all_defs = outcome_data.get("definitions", [])
                pairs    = []
                used     = set()
                for defn in all_defs:
                    m = re.match(
                        r'^([A-Za-z][A-Za-z0-9\s\.\(\)/\-]{2,35}?)\s+'
                        r'(is a|is an|is the|refers to|means |defined as)\s+(.+)',
                        defn
                    )
                    if m:
                        term     = m.group(1).strip()
                        desc     = (m.group(2)+" "+m.group(3)).strip()[:110]
                        term_low = term.lower()
                        if (not any(ex in term_low for ex in EXCLUDE_TERMS) and
                            not re.search(r'\d', term) and
                            len(term) > 3 and
                            term_low not in used and
                            len(pairs) < 4):
                            used.add(term_low)
                            pairs.append({"term": term, "description": desc})
                if len(pairs) < 4:
                    for t, d in desc_map.items():
                        if t not in used and len(pairs) < 4:
                            if not any(ex in t.lower() for ex in EXCLUDE_TERMS):
                                pairs.append({"term": t.capitalize(), "description": d[:110]})
                                used.add(t)
                question       = "Match each term in Column A with its correct description in Column B."
                options        = pairs[:4]
                correct_answer = " | ".join([f"{j+1}. {p['term']}" for j, p in enumerate(pairs[:4])])

            # ── Open ──────────────────────────────────────────────
            else:
                section_lines = outcome_data.get("indicative_sections", {}).get(section, [])
                steps         = [l for l in section_lines if re.match(r'^\d+[\.\)]\s+[A-Z]', l)][:3]
                commands      = [l for l in section_lines if CODE_RE.search(l)][:2]
                open_templates = {
                    'remember'  : f"Define {topic} and explain its role in {phrase}.",
                    'understand': f"Explain how {topic} works in the context of {phrase}.",
                    'apply'     : f"Demonstrate how to use {topic} when {phrase}. Provide a step-by-step explanation.",
                    'analyze'   : f"Analyze the importance of {topic} in {phrase}. Identify advantages and limitations.",
                    'evaluate'  : f"Evaluate the effectiveness of {topic} when {phrase}. Justify with examples.",
                    'create'    : f"Design a solution using {topic} that demonstrates {phrase}. Explain your decisions.",
                }
                question = open_templates.get(bloom, open_templates['apply'])
                hints    = []
                if steps:    hints.append("Key steps: " + " | ".join(steps))
                if commands: hints.append("Commands: " + " | ".join(commands))
                hints.append(f"Award marks for correct explanation of {topic} in context.")
                correct_answer = " ".join(hints)

            # ── Marks ─────────────────────────────────────────────
            raw_marks = {'true_false':2,'matching':4,'mcq':2,'open':7}[qtype]

            all_questions.append({
                "number"          : q_number,
                "learning_outcome": outcome,
                "bloom_level"     : bloom,
                "question_type"   : qtype,
                "question"        : question,
                "options"         : options,
                "correct_answer"  : correct_answer,
                "marks"           : raw_marks,
                "topic"           : topic,
                "section"         : section,
            })
            q_number += 1

    df_exam   = pd.DataFrame(all_questions)

    # ── Scale marks to exact total ─────────────────────────────────
    raw_total = df_exam['marks'].sum()
    if raw_total > 0:
        df_exam['marks'] = df_exam['marks'].apply(
            lambda m: round((m / raw_total) * request.total_marks)
        )
        diff = request.total_marks - df_exam['marks'].sum()
        if diff != 0:
            idx = (df_exam[df_exam['question_type']=='open']['marks'].idxmax()
                   if not df_exam[df_exam['question_type']=='open'].empty
                   else df_exam['marks'].idxmax())
            df_exam.at[idx, 'marks'] += diff

    # ── Save to database ───────────────────────────────────────────
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
    db.add(exam_db)
    db.commit()
    db.refresh(exam_db)

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

# ── DOWNLOAD EXAM PDF ─────────────────────────────────────────────────
@app.get("/exams/{exam_id}/pdf")
def download_exam_pdf(
    exam_id: int,
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "Exam not found")

    questions = db.query(Question).filter(Question.exam_id == exam_id).all()
    if not questions:
        raise HTTPException(404, "No questions found for this exam")

    # Build DataFrame from DB
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

    df = pd.DataFrame(rows)
    csv_path = f"temp_exam_{exam_id}.csv"
    pdf_path = f"exam_{exam_id}.pdf"
    df.to_csv(csv_path, index=False)

    from pdf_builder import build_exam_pdf
    build_exam_pdf(
        exam_csv        = csv_path,
        output_path     = pdf_path,
        school_name     = "RWANDA TVET BOARD",
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
    return FileResponse(pdf_path, media_type="application/pdf",
                        filename=f"exam_{exam.module}_{exam_id}.pdf")


# ── DOWNLOAD MARKING GUIDE PDF ────────────────────────────────────────
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
    return FileResponse(pdf_path, media_type="application/pdf",
                        filename=f"marking_guide_{exam_id}.pdf")


# ── QUESTION BANK ─────────────────────────────────────────────────────
@app.get("/question-bank", response_model=list[QuestionBankItem])
def get_question_bank(
    module  : str     = None,
    level   : int     = None,
    qtype   : str     = None,
    bloom   : str     = None,
    skip    : int     = 0,
    limit   : int     = 50,
    db      : Session = Depends(get_db),
    teacher : Teacher = Depends(get_current_teacher),
):
    query = db.query(QuestionBank)
    if module : query = query.filter(QuestionBank.module.ilike(f"%{module}%"))
    if level  : query = query.filter(QuestionBank.level  == level)
    if qtype  : query = query.filter(QuestionBank.question_type == qtype)
    if bloom  : query = query.filter(QuestionBank.bloom_level   == bloom)
    return query.offset(skip).limit(limit).all()


@app.get("/exams", response_model=list[dict])
def get_my_exams(
    db     : Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher),
):
    exams = db.query(Exam).filter(Exam.teacher_id == teacher.id)\
               .order_by(Exam.created_at.desc()).all()
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