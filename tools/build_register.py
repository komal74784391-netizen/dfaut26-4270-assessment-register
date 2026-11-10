"""Reference implementation of the DFAUT26-4270 term register builder.

Input: a JSON snapshot with one entry per course:

    [
      {
        "course_code": "...",
        "assignments": [{"name": "...", "due_at": "...", "is_quiz_assignment": false}, ...],
        "quizzes": [{"title": "...", "quiz_type": "...", "due_at": "..."}, ...]
      }
    ]

Output: the assessment_register.csv rows used by the program office.

The scope manifest in ``config/register_scope.json`` is authoritative.  In
particular, the inclusion rule keeps every quiz in a scoped course, independent
of its quiz type or publication state, while skipping the placeholder
assignment records that the platform materialises for graded quizzes.
"""

import csv
import json
import sys

GRADED_QUIZ_TYPES = ("assignment", "graded_survey")


def graded_flag(item_kind, item):
    if item_kind == "assignment":
        return "yes"
    return "yes" if item.get("quiz_type") in GRADED_QUIZ_TYPES else "no"


def build_rows(snapshot):
    rows = []
    for course in snapshot:
        assignments = [
            a for a in course.get("assignments", []) if not a.get("is_quiz_assignment")
        ]
        for a in assignments:
            rows.append(
                [course["course_code"], "assignment", a["name"], a.get("due_at", "")[:10],
                 graded_flag("assignment", a)]
            )
        for q in course.get("quizzes", []):
            rows.append(
                [course["course_code"], "quiz", q["title"], q.get("due_at", "")[:10],
                 graded_flag("quiz", q)]
            )
    rows.sort(key=lambda r: (r[0], 0 if r[1] == "assignment" else 1, r[2]))
    return rows


def main():
    snapshot = json.load(open(sys.argv[1], encoding="utf-8"))
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["course_code", "item_kind", "item_name", "due_date", "graded"])
        writer.writerows(build_rows(snapshot))


if __name__ == "__main__":
    main()
