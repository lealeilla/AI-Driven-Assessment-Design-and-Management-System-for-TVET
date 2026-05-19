export const quickStats = [
  {
    title: "Exams Generated",
    value: "28",
    change: "6 new papers prepared this week",
    accent: "bg-blue-100 text-blue-700"
  },
  {
    title: "Scripts Marked",
    value: "184",
    change: "42 moderated by teachers",
    accent: "bg-emerald-100 text-emerald-700"
  },
  {
    title: "Pending Review",
    value: "12",
    change: "Awaiting teacher approval",
    accent: "bg-amber-100 text-amber-700"
  },
  {
    title: "Pass Rate",
    value: "81%",
    change: "Across recent competency checks",
    accent: "bg-cyan-100 text-cyan-700"
  }
];

export const levels = ["Level 3", "Level 4", "Level 5"];

export const programs = [
  "Software Development",
  "Networking and Internet Technology",
  "Electrical Technology",
  "Building Construction"
];

export const modulesByProgram = {
  "Software Development": [
    "Frontend Development",
    "Database Design",
    "Software Testing"
  ],
  "Networking and Internet Technology": [
    "Computer Networking",
    "Server Administration",
    "Cybersecurity Fundamentals"
  ],
  "Electrical Technology": [
    "Electrical Installation",
    "Industrial Maintenance",
    "Safety and Compliance"
  ],
  "Building Construction": [
    "Construction Technology",
    "Technical Drawing",
    "Site Supervision"
  ]
};

export const generatorSteps = [
  "Curriculum competencies and module outcomes are matched first.",
  "Past exam papers are reviewed to keep structure familiar and paper-based.",
  "Questions are arranged from lower-order to higher-order Bloom's Taxonomy thinking.",
  "Teachers review and edit the final paper before download and use."
];

export const bloomStages = [
  { name: "Remember", focus: "Recall key concepts and terms" },
  { name: "Understand", focus: "Explain ideas in the module context" },
  { name: "Apply", focus: "Use knowledge in a practical scenario" },
  { name: "Analyze", focus: "Break down technical situations" },
  { name: "Evaluate", focus: "Justify decisions and compare solutions" }
];

export const generatedExam = {
  institution: "IPRC Kigali - TVET Assessment Unit",
  module: "Frontend Development",
  level: "Level 4",
  duration: "2 Hours 30 Minutes",
  instructions: [
    "Answer all questions in the spaces provided on the paper.",
    "The paper was generated from curriculum outcomes and past exam structure.",
    "Questions progress from lower-order to higher-order thinking based on Bloom's Taxonomy."
  ],
  sections: [
    {
      title: "Section A: Multiple Choice",
      type: "Multiple Choice",
      note: "Choose the most appropriate answer.",
      questions: [
        {
          id: 1,
          text: "Which React feature helps teachers reuse the same layout across multiple assessment screens?",
          marks: 2,
          answerSpace: "Short answer space"
        },
        {
          id: 2,
          text: "Which file type is most suitable for downloading a paper-based examination?",
          marks: 2,
          answerSpace: "Short answer space"
        }
      ]
    },
    {
      title: "Section B: True / False",
      type: "True/False",
      note: "Write True or False in the blank provided.",
      questions: [
        {
          id: 3,
          text: "AI-generated marking suggestions can be published without teacher validation.",
          marks: 2,
          answerSpace: "Single line response"
        },
        {
          id: 4,
          text: "Paper-based exams can still use AI during design and marking workflows.",
          marks: 2,
          answerSpace: "Single line response"
        }
      ]
    },
    {
      title: "Section C: Matching",
      type: "Matching",
      note: "Match the concept in Column A with the best description in Column B.",
      questions: [
        {
          id: 5,
          text: "Match Bloom's levels to the correct classroom task.",
          marks: 6,
          answerSpace: "Structured table space"
        }
      ]
    },
    {
      title: "Section D: Open-Ended Questions",
      type: "Open-ended",
      note: "Show reasoning clearly. Use the lined answer area.",
      questions: [
        {
          id: 6,
          text: "Explain how curriculum data and past papers can be combined to generate a balanced paper-based assessment for software development.",
          marks: 10,
          answerSpace: "Large lined writing area"
        },
        {
          id: 7,
          text: "Evaluate the benefits and risks of using AI-assisted marking in a teacher-controlled TVET assessment workflow.",
          marks: 16,
          answerSpace: "Extended lined writing area"
        }
      ]
    }
  ]
};

export const generatedExamList = [
  {
    id: "EX-2404",
    title: "Frontend Development Mid-Term",
    module: "Frontend Development",
    level: "Level 4",
    status: "Ready for PDF",
    date: "29 Apr 2026"
  },
  {
    id: "EX-2405",
    title: "Database Design End-of-Module",
    module: "Database Design",
    level: "Level 5",
    status: "Needs Review",
    date: "28 Apr 2026"
  },
  {
    id: "EX-2406",
    title: "Computer Networking Theory Paper",
    module: "Computer Networking",
    level: "Level 3",
    status: "Ready for PDF",
    date: "27 Apr 2026"
  }
];

export const uploadQueue = [
  {
    id: 1,
    student: "Uwase Aline",
    file: "aline_frontend_script.pdf",
    status: "AI extraction complete"
  },
  {
    id: 2,
    student: "Niyonzima Eric",
    file: "eric_midterm_scan.jpg",
    status: "Waiting for teacher review"
  }
];

export const markingRows = [
  {
    id: 1,
    question: "Q1",
    answer: "Reusable components keep page structure consistent and reduce repeated code across dashboard screens.",
    aiMark: 8,
    finalMark: 8
  },
  {
    id: 2,
    question: "Q2",
    answer: "PDF is best because it preserves formatting and answer space for printing and scanning.",
    aiMark: 9,
    finalMark: 10
  },
  {
    id: 3,
    question: "Q3",
    answer: "AI can speed up first marking, but the teacher must confirm accuracy and fairness before approval.",
    aiMark: 13,
    finalMark: 13
  }
];

export const competencyPerformance = [
  { label: "UI Design", value: 84 },
  { label: "Problem Solving", value: 76 },
  { label: "Documentation", value: 62 },
  { label: "Technical Accuracy", value: 81 },
  { label: "Evaluation Skills", value: 69 }
];

export const strengthWeakness = [
  { area: "Strong: Practical application", strong: 86, weak: 14 },
  { area: "Strong: Core concept recall", strong: 78, weak: 22 },
  { area: "Weak: Written justification", strong: 54, weak: 46 }
];

export const analyticsSummary = [
  { title: "Average Score", value: "68%", note: "Across marked scripts" },
  { title: "Pass Rate", value: "81%", note: "Teacher-validated results only" },
  { title: "Competencies Tracked", value: "14", note: "Supports competency-based assessment analysis." }
];
