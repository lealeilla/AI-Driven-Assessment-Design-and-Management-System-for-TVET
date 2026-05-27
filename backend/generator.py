import json, re, random, os

# ── Question templates per Bloom level ──────────────────────────────────
MCQ_TEMPLATES = {
    'remember'  : [
        "Which of the following correctly defines {topic}?",
        "What does {topic} stand for in {module}?",
        "Which statement about {topic} is correct?",
        "{topic} is best described as:",
    ],
    'understand': [
        "What is the main purpose of {topic} in {module}?",
        "Which statement best explains how {topic} works?",
        "What role does {topic} play when {phrase}?",
        "How does {topic} contribute to {phrase}?",
    ],
    'apply': [
        "Which command or method is used to {phrase} with {topic}?",
        "How would you correctly use {topic} when {phrase}?",
        "Which step is correct when using {topic} to {phrase}?",
        "What is the correct way to implement {topic}?",
    ],
    'analyze': [
        "What is the key difference between {topic} and similar alternatives?",
        "Which factor most affects the performance of {topic}?",
        "Why is {topic} preferred when {phrase}?",
        "What would happen if {topic} is missing when {phrase}?",
    ],
    'evaluate': [
        "Which approach using {topic} is most effective when {phrase}?",
        "What is the best reason to use {topic} when {phrase}?",
        "Which limitation of {topic} must be considered when {phrase}?",
    ],
    'create': [
        "How would you design a solution using {topic} to {phrase}?",
        "Which combination of tools including {topic} is best for {phrase}?",
    ],
}

TF_TEMPLATES_TRUE = [
    "{topic} is used to {short_phrase}.",
    "{topic} is an essential component when {phrase}.",
    "{topic} helps developers to {short_phrase} effectively.",
    "Using {topic} improves the process of {phrase}.",
    "{topic} must be configured before you can {short_phrase}.",
]

TF_TEMPLATES_FALSE = [
    "{topic} is not needed when {phrase}.",
    "{topic} replaces the need for any security when {phrase}.",
    "{topic} cannot be used together with other tools when {phrase}.",
    "{topic} is only used for front-end development, never for {phrase}.",
    "You can {short_phrase} without ever using {topic}.",
]

OPEN_TEMPLATES = {
    'remember': [
        "Define {topic} and explain its role in {phrase}.",
        "List and briefly describe the key components of {topic} used when {phrase}.",
    ],
    'understand': [
        "Explain how {topic} works in the context of {phrase}.",
        "Describe the relationship between {topic} and {phrase}. Give an example.",
    ],
    'apply': [
        "Demonstrate step-by-step how to use {topic} when {phrase}.",
        "Write a practical example showing how {topic} is applied when {phrase}.",
        "Show how you would implement {topic} to {phrase}. Include key steps.",
    ],
    'analyze': [
        "Analyze the role of {topic} in {phrase}. Identify its advantages and limitations.",
        "Compare {topic} with at least one alternative and explain which is better for {phrase}.",
    ],
    'evaluate': [
        "Evaluate the effectiveness of {topic} when {phrase}. Justify your answer with examples.",
        "Assess the impact of {topic} on {phrase}. What would change if {topic} was not used?",
    ],
    'create': [
        "Design a solution that uses {topic} to {phrase}. Explain your design decisions.",
        "Develop a plan for {phrase} using {topic}. Include tools, steps, and expected results.",
    ],
}


def get_short_phrase(phrase: str) -> str:
    """Extract a short action from the phrase for True/False use."""
    # Remove common gerund starters
    for starter in ['developing','securing','testing','managing',
                    'preparing','writing','applying','performing',
                    'designing','planning','setting up']:
        if phrase.lower().startswith(starter):
            return phrase[len(starter):].strip()
    return phrase


def generate_mcq(topic, bloom, phrase, module, all_terms):
    templates   = MCQ_TEMPLATES.get(bloom, MCQ_TEMPLATES['understand'])
    question    = random.choice(templates).format(
        topic=topic, phrase=phrase, module=module
    )
    # Build distractors from real module terms — not the correct answer
    distractors = [t for t in all_terms if t.lower() != topic.lower()]
    random.shuffle(distractors)
    distractors = distractors[:3]

    # If not enough distractors, use generic plausible ones
    while len(distractors) < 3:
        distractors.append("None of the above")

    opts_list = [topic] + distractors
    random.shuffle(opts_list)
    letters  = ['A', 'B', 'C', 'D']
    options  = [f"{letters[i]}. {opts_list[i]}" for i in range(len(opts_list))]
    correct  = letters[opts_list.index(topic)]
    return question, options, correct


def generate_true_false(topic, phrase, index):
    short_phrase = get_short_phrase(phrase)
    # Alternate true and false
    if index % 2 == 0:
        q = random.choice(TF_TEMPLATES_TRUE).format(
            topic=topic, phrase=phrase, short_phrase=short_phrase
        )
        correct = "A"
    else:
        q = random.choice(TF_TEMPLATES_FALSE).format(
            topic=topic, phrase=phrase, short_phrase=short_phrase
        )
        correct = "B"
    return q, ["A. True", "B. False"], correct


def generate_matching(outcome_data, desc_map):
    """
    Build 4 matching pairs from the manual definitions.
    Uses both inline definitions and desc_map.
    """
    pairs = []
    used  = set()

    # Try definitions from manual first
    for defn in outcome_data.get("definitions", []):
        if len(pairs) >= 4:
            break
        m = re.match(
            r'^([A-Za-z][A-Za-z0-9\s\.\(\)/\-]{2,45}?)\s+'
            r'(is a|is an|is the|refers to|means |defined as|stands for)\s+(.+)',
            defn
        )
        if m:
            term = m.group(1).strip()
            desc = (m.group(2) + " " + m.group(3)).strip()
            # Cut to one clean sentence
            if len(desc) > 150:
                sentences = re.split(r'(?<=[.!?])\s+', desc[:200])
                desc = sentences[0] if sentences else desc[:150]
            term_low = term.lower()
            first_w  = term.split()[0].lower()
            # Skip verbs, generics, company names
            bad = {'data','process','system','method','tool','it','this','that',
                   'analyze','configure','apply','test','design','implement',
                   'use','run','build','create'}
            if (term_low not in used and
                    term[0].isupper() and
                    first_w not in bad and
                    len(term) > 3 and
                    'mietech' not in term_low and
                    'rwanda' not in term_low):
                used.add(term_low)
                pairs.append({"term": term, "description": desc})

    # Pad from desc_map if needed
    if len(pairs) < 4:
        for term, desc in desc_map.items():
            if len(pairs) >= 4:
                break
            t_low   = term.lower().strip()
            first_w = term.split()[0].lower()
            bad     = {'data','process','system','method','tool','it','this',
                       'analyze','configure','apply','test','design','implement'}
            if t_low not in used and first_w not in bad and len(term) > 3:
                clean_desc = re.sub(r'\s+', ' ', str(desc)).strip()
                if len(clean_desc) > 150:
                    sentences = re.split(r'(?<=[.!?])\s+', clean_desc[:200])
                    clean_desc = sentences[0] if sentences else clean_desc[:150]
                used.add(t_low)
                pairs.append({
                    "term"       : term.strip().capitalize(),
                    "description": clean_desc,
                })

    # Deduplicate
    seen, unique = set(), []
    for p in pairs:
        if p['term'].lower() not in seen:
            seen.add(p['term'].lower())
            unique.append(p)

    question = "Match each term in Column A with its correct description in Column B."
    options  = unique[:4]
    correct  = " | ".join([f"{i+1}→{chr(65+i)}" for i in range(len(options))])
    return question, options, correct


def generate_open(topic, bloom, phrase):
    templates = OPEN_TEMPLATES.get(bloom, OPEN_TEMPLATES['apply'])
    question  = random.choice(templates).format(topic=topic, phrase=phrase)
    correct   = (
        f"Award marks for: correct explanation of {topic}, "
        f"relevant example or steps, and connection to {phrase}."
    )
    return question, [], correct


def scale_marks_to_total(questions: list, total_marks: int) -> list:
    if not questions:
        return questions
    raw_total = sum(q.get("marks", 2) for q in questions)
    if raw_total == 0:
        return questions
    for q in questions:
        q["marks"] = max(1, round((q["marks"] / raw_total) * total_marks))
    diff = total_marks - sum(q["marks"] for q in questions)
    if diff != 0:
        open_qs = [q for q in questions if q["question_type"] == "open"]
        target  = (max(open_qs, key=lambda q: q["marks"])
                   if open_qs else max(questions, key=lambda q: q["marks"]))
        target["marks"] = max(1, target["marks"] + diff)
    return questions


def generate_exam_questions(
    outcome      : str,
    outcome_data : dict,
    desc_map     : dict,
    valid_terms  : list,
    all_terms    : list,
    count        : int,
    module       : str,
    phrase       : str,
    bloom_map    : dict,
) -> list:
    """
    Generate `count` questions for one learning outcome.
    Uses manual definitions and terms directly.
    """
    # Build bloom sequence
    bloom_seq = []
    for lvl, n in bloom_map.items():
        bloom_seq.extend([lvl] * n)
    while len(bloom_seq) < count: bloom_seq.append('apply')
    bloom_seq = bloom_seq[:count]
    random.shuffle(bloom_seq)

    # Build type sequence
    n_mcq  = max(1, int(count * 0.35))
    n_tf   = max(1, int(count * 0.20))
    n_mat  = max(1, int(count * 0.10))
    n_open = count - n_mcq - n_tf - n_mat
    if n_open < 1: n_open = 1
    type_seq = (['mcq'] * n_mcq +
                ['true_false'] * n_tf +
                ['matching'] * n_mat +
                ['open'] * n_open)
    while len(type_seq) < count: type_seq.append('open')
    type_seq = type_seq[:count]
    random.shuffle(type_seq)

    questions    = []
    match_done   = False  # Only generate matching once per outcome
    term_index   = 0

    for i in range(count):
        bloom = bloom_seq[i]
        qtype = type_seq[i]

        # Pick topic — rotate through valid terms
        topic = valid_terms[term_index % len(valid_terms)]
        term_index += 1

        if qtype == 'matching':
            if match_done:
                # Replace with open if matching already used
                qtype = 'open'
            else:
                match_done = True

        raw_marks = {'true_false': 2, 'matching': 4, 'mcq': 2, 'open': 7}[qtype]

        if qtype == 'mcq':
            question, options, correct = generate_mcq(topic, bloom, phrase, module, all_terms)

        elif qtype == 'true_false':
            question, options, correct = generate_true_false(topic, phrase, i)

        elif qtype == 'matching':
            question, options, correct = generate_matching(outcome_data, desc_map)

        else:
            question, options, correct = generate_open(topic, bloom, phrase)

        questions.append({
            "learning_outcome": outcome,
            "bloom_level"     : bloom,
            "question_type"   : qtype,
            "question"        : question,
            "options"         : options,
            "correct_answer"  : correct,
            "marks"           : raw_marks,
            "topic"           : topic,
            "section"         : "General",
        })

    return questions