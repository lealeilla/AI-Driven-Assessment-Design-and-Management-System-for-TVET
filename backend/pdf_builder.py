from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pandas as pd, ast
import re


def build_exam_pdf(exam_csv, output_path, school_name, program, module,
                   level, exam_date, time_allowed, total_marks,
                   assessment_type, outcomes):

    df = pd.read_csv(exam_csv)
    if total_marks is None:
        total_marks = int(df['marks'].sum())

    doc   = SimpleDocTemplate(output_path, pagesize=A4,
                               topMargin=1.8*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    story = []
    S     = lambda name, **kw: ParagraphStyle(name, **kw)

    story += [
        Paragraph(school_name,
                  S('sc', fontSize=13, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("COMPETENCY-BASED ASSESSMENT",
                  S('ti', fontSize=11, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(f"[ {assessment_type.upper()} ASSESSMENT ]",
                  S('at', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        HRFlowable(width="100%", thickness=1.5, color=colors.black),
        Spacer(1, 4),
    ]

    meta = S('me', fontSize=10, fontName='Helvetica')
    story += [
        Paragraph(f"<b>Program:</b> {program}  |  <b>Level:</b> {level}"
                  f"  |  <b>Total Marks:</b> {total_marks}", meta),
        Paragraph(f"<b>Module:</b> {module}  |  <b>Date:</b> {exam_date}"
                  f"  |  <b>Time:</b> {time_allowed}", meta),
        Spacer(1, 4),
        Paragraph("Name: ___________________________  "
                  "Index No: ______________  Class: ________",
                  S('ci', fontSize=10, fontName='Helvetica')),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=0.5, color=colors.grey),
        Spacer(1, 8),
    ]

    section_map = {
        'true_false': ('SECTION A: TRUE / FALSE',
                       'Answer True (T) or False (F).'),
        'mcq':        ('SECTION B: MULTIPLE CHOICE',
                       'Choose ONE correct answer and circle the letter.'),
        'matching':   ('SECTION C: MATCHING',
                       'Match each term in Column A with Column B.'),
        'open':       ('SECTION D: OPEN-ENDED',
                       'Answer ALL questions. Write in the spaces provided.'),
    }

    q_no = 1
    for qtype in ['true_false', 'mcq', 'matching', 'open']:
        rows = df[df['question_type'] == qtype]
        if rows.empty:
            continue

        title, instr = section_map[qtype]
        story += [
            HRFlowable(width="100%", thickness=0.8, color=colors.black),
            Paragraph(title, S('sh', fontSize=11, fontName='Helvetica-Bold',
                                spaceBefore=10, spaceAfter=4)),
            Paragraph(instr, S('si', fontSize=9, fontName='Helvetica-Oblique',
                                spaceAfter=6,
                                textColor=colors.HexColor('#444444'))),
        ]

        for _, row in rows.iterrows():
            marks = int(row['marks'])
            qt    = [[
                Paragraph(f"<b>{q_no}.</b>",
                           S('qn', fontSize=10, fontName='Helvetica-Bold')),
                Paragraph(str(row['question']),
                           S('qt', fontSize=10, fontName='Helvetica', leading=14)),
                Paragraph(f"({marks} marks)",
                           S('qm', fontSize=9, fontName='Helvetica-Bold',
                             alignment=TA_RIGHT)),
            ]]
            story.append(Table(qt, colWidths=[0.7*cm, 14.3*cm, 2.5*cm],
                               style=[('VALIGN', (0,0), (-1,-1), 'TOP'),
                                      ('PADDING', (0,0), (-1,-1), 2)]))

            if qtype == 'true_false':
                story.append(Paragraph(
                    "&nbsp;&nbsp;Answer: <b>True &nbsp;&nbsp; False</b>",
                    S('tf', fontSize=10, fontName='Helvetica',
                      leftIndent=20, spaceAfter=6)
                ))

            elif qtype == 'mcq':
                try:
                    opts = ast.literal_eval(str(row['options']))
                except:
                    opts = ["A. Option 1", "B. Option 2",
                            "C. Option 3", "D. Option 4"]
                for opt in opts:
                    story.append(Paragraph(str(opt),
                        S('op', fontSize=10, fontName='Helvetica', leftIndent=20)))
                story.append(Paragraph("Answer: _______",
                    S('op2', fontSize=10, fontName='Helvetica',
                      leftIndent=20, spaceAfter=6)))
                
            elif qtype == 'matching':
                try:
                    pairs = ast.literal_eval(str(row['options']))
                except:
                    pairs = []
                if pairs:
                    from reportlab.platypus import KeepTogether

                    # Build full matching table — kept together on same page
                    td = [["Column A (Terms)", "Column B (Descriptions)"]]
                    for j, p in enumerate(pairs):
                        term = p.get('term', '') if isinstance(p, dict) else str(p)
                        desc = p.get('description', '') if isinstance(p, dict) else ''

                        # Clean and trim description properly
                        desc = str(desc).strip()
                        if len(desc) > 150:
                            desc = desc[:147] + "..."

                        td.append([
                            Paragraph(f"{j+1}. {term}",
                                S('mt', fontSize=9, fontName='Helvetica', leading=13)),
                            Paragraph(f"{'ABCD'[j]}. {desc}",
                                S('md', fontSize=9, fontName='Helvetica', leading=13)),
                        ])

                    mt = Table(td, colWidths=[8*cm, 9*cm])
                    mt.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0),  colors.HexColor('#EEEEEE')),
                        ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
                        ('FONTSIZE',   (0,0), (-1,-1), 9),
                        ('BOX',        (0,0), (-1,-1), 0.5, colors.grey),
                        ('INNERGRID',  (0,0), (-1,-1), 0.3, colors.grey),
                        ('PADDING',    (0,0), (-1,-1), 6),
                        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1),
                        [colors.white, colors.HexColor('#FAFAFA')]),
                    ]))

                    # KeepTogether prevents the table splitting across pages
                    story += [
                        Spacer(1, 4),
                        KeepTogether([mt]),
                    ]

                story.append(Paragraph(
                    "Answers: 1.___  2.___  3.___  4.___",
                    S('ma', fontSize=10, fontName='Helvetica',
                    leftIndent=20, spaceAfter=6)
                ))

            elif qtype == 'open':
                num_lines = min(max(marks // 2, 3), 10)
                for _ in range(num_lines):
                    story.append(HRFlowable(
                        width="90%", thickness=0.4,
                        color=colors.HexColor('#BBBBBB'), spaceAfter=8
                    ))
                story.append(Spacer(1, 4))

            q_no += 1

    story += [
        HRFlowable(width="100%", thickness=1, color=colors.black),
        Spacer(1, 4),
        Paragraph(
            f"END OF EXAMINATION | {assessment_type} | {module} | Total: {total_marks} marks",
            S('fo', fontSize=8, fontName='Helvetica', alignment=TA_CENTER,
              textColor=colors.HexColor('#666666'))
        ),
    ]

    doc.build(story)
    print(f"Exam PDF saved: {output_path}")


def build_marking_guide_pdf(df_answers, output_path, module, program,
                             level, total_marks, exam_date, assessment_type):

    doc   = SimpleDocTemplate(output_path, pagesize=A4,
                               topMargin=1.8*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    story = []
    S     = lambda name, **kw: ParagraphStyle(name, **kw)

    story += [
        Paragraph("RWANDA TVET BOARD",
                  S('sc', fontSize=13, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("MARKING GUIDE — CONFIDENTIAL",
                  S('ti', fontSize=11, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(f"[ {assessment_type.upper()} ASSESSMENT ]",
                  S('at', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        HRFlowable(width="100%", thickness=1.5, color=colors.black),
        Spacer(1, 6),
        Paragraph(f"<b>Module:</b> {module}  |  <b>Program:</b> {program}"
                  f"  |  <b>Level:</b> {level}  |  <b>Total Marks:</b> {total_marks}",
                  S('me', fontSize=10, fontName='Helvetica')),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=0.5, color=colors.grey),
        Spacer(1, 8),
    ]

    section_colors = {
        'true_false': '#D6EAF8',
        'mcq'       : '#D5F5E3',
        'matching'  : '#FDEBD0',
        'open'      : '#F4ECF7',
    }

    for _, row in df_answers.iterrows():
        qtype = str(row['question_type'])
        marks = int(row['marks'])
        bg    = colors.HexColor(section_colors.get(qtype, '#FFFFFF'))

        content = [
            [Paragraph(f"<b>Q{row['number']}.</b>",
                        S('qn', fontSize=10, fontName='Helvetica-Bold')),
             Paragraph(str(row['question']),
                        S('qt', fontSize=10, fontName='Helvetica', leading=14)),
             Paragraph(f"({marks} marks)",
                        S('qm', fontSize=9, fontName='Helvetica-Bold',
                          alignment=TA_RIGHT))],
            [Paragraph("", S('x', fontSize=9)),
             Paragraph(f"<b>Answer:</b> {str(row.get('model_answer',''))[:400]}",
                        S('an', fontSize=10, fontName='Helvetica-Oblique',
                          leading=13, leftIndent=10,
                          textColor=colors.HexColor('#1a5276'))),
             Paragraph("", S('x2', fontSize=9))],
            [Paragraph("", S('x3', fontSize=9)),
             Paragraph(f"<b>Marking guide:</b> {str(row.get('marks_guide',''))}",
                        S('mg', fontSize=9, fontName='Helvetica',
                          leading=13, leftIndent=10,
                          textColor=colors.HexColor('#145a32'))),
             Paragraph("", S('x4', fontSize=9))],
        ]

        qt = Table(content, colWidths=[0.8*cm, 14*cm, 2.7*cm])
        qt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('VALIGN',     (0,0), (-1,-1), 'TOP'),
            ('PADDING',    (0,0), (-1,-1), 5),
            ('BOX',        (0,0), (-1,-1), 0.3, colors.grey),
            ('LINEBELOW',  (0,0), (-1,0),  0.5, colors.grey),
        ]))
        story += [qt, Spacer(1, 6)]

    story += [
        HRFlowable(width="100%", thickness=1, color=colors.black),
        Spacer(1, 4),
        Paragraph(
            f"MARKING GUIDE | {module} | Total: {total_marks} marks | CONFIDENTIAL",
            S('fo', fontSize=8, fontName='Helvetica', alignment=TA_CENTER,
              textColor=colors.HexColor('#666666'))
        ),
    ]

    doc.build(story)
    print(f"Marking guide saved: {output_path}")