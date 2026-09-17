# Curriculum specification

The 71 requested modules remain the full curriculum target. v0.1 combines selected foundations into 12 lessons; a matching lesson below does not imply complete coverage of the original module. Each available lesson has objectives, explanatory sections, five questions with option-specific feedback and linked practical tasks.

## Available lesson sequence

| Lesson | Area | Questions | Challenges |
|---|---|---|---|
| Первая строка Python (`python-start`) | 01 · Основы Python | 5 | python-revenue |
| Функции и надёжные расчёты (`functions`) | 01 · Основы Python | 5 | conversion |
| NumPy: думать массивами (`numpy`) | 02 · NumPy | 5 | numpy-mask |
| Знакомство с DataFrame (`pandas-intro`) | 03 · pandas | 5 | select-columns |
| Фильтрация данных (`pandas-filtering`) | 03 · pandas | 5 | filter-orders, sort-orders |
| Выручка по городам (`groupby`) | 03 · pandas | 5 | revenue-city, aov, customer-summary |
| Качество данных: пропуски и дубликаты (`cleaning`) | 04 · Подготовка данных | 5 | clean-cities, fill-missing |
| Объединение таблиц и даты (`joins-dates`) | 04 · Подготовка данных | 5 | customer-summary |
| EDA: сначала вопросы, затем выводы (`eda`) | 05 · Исследование данных | 5 | median |
| График, который отвечает на вопрос (`visualization`) | 06 · Визуализация | 5 | monthly-plot |
| Статистика без ложной уверенности (`statistics`) | 07 · Статистика | 5 | conversion, median |
| SQL и pandas: один анализ, два инструмента (`sql`) | 08 · SQL + Python | 5 | sql-revenue |

## Full target sequence

Every module below is **In Progress** as a curriculum objective or **Planned** where absent. None is claimed complete at the full specification depth.

1. INTRODUCTION TO PYTHON
2. BASIC DATA TYPES
3. OPERATORS
4. STRINGS FOR ANALYSTS
5. CONDITIONS
6. LOOPS
7. LISTS
8. TUPLES, SETS, DICTIONARIES
9. COMPREHENSIONS
10. FUNCTIONS
11. ERRORS AND EXCEPTIONS
12. FILES
13. CSV
14. JSON
15. JUPYTER WORKFLOW
16. NUMPY INTRODUCTION
17. NUMPY INDEXING
18. NUMPY OPERATIONS
19. NUMPY AGGREGATIONS
20. NUMPY MISSING VALUES
21. NUMPY PERFORMANCE CONCEPT
22. PANDAS INTRODUCTION
23. READING DATA WITH PANDAS
24. DATAFRAME SELECTION
25. FILTERING
26. SORTING
27. CREATING COLUMNS
28. MISSING DATA
29. DUPLICATES
30. DATA TYPES
31. STRING OPERATIONS IN PANDAS
32. DATETIME IN PANDAS
33. GROUPBY
34. MULTIPLE AGGREGATIONS
35. VALUE COUNTS
36. MERGE
37. JOIN ERRORS
38. CONCAT
39. PIVOT TABLES
40. RESHAPING
41. PANDAS INDEX
42. DATA CLEANING PROJECT
43. EXPLORATORY DATA ANALYSIS
44. DESCRIPTIVE STATISTICS
45. MEAN VS MEDIAN
46. DISTRIBUTIONS
47. OUTLIERS
48. CORRELATION
49. MATPLOTLIB
50. CHOOSING A CHART
51. SEABORN
52. VISUALIZATION QUALITY
53. MISLEADING VISUALIZATION
54. BASIC STATISTICS FOR ANALYST
55. PROBABILITY BASICS
56. CONFIDENCE INTERVAL CONCEPT
57. HYPOTHESIS TESTING INTRO
58. SCIPY FOR ANALYSTS
59. A/B TEST BASICS
60. SQL INTRODUCTION
61. SQL + PANDAS
62. EXCEL
63. API DATA
64. DATA FROM API
65. REGULAR EXPRESSIONS
66. DATA QUALITY
67. REPRODUCIBLE ANALYSIS
68. PERFORMANCE BASICS
69. DEBUGGING DATA CODE
70. CLEAN ANALYTICAL CODE
71. FINAL JUNIOR PROJECT

## Assessment design

Current question format is single-choice. Practical contracts cover scalars, arrays, DataFrames, SQL tables and one-axis line charts. Mastery combines latest quiz correctness (30%) and unique practical completions (70%). Reading a lesson records completion but does not prove mastery. Daily practice and due mistake review use existing content, not additional counted questions.

Seven topic sets reuse lesson questions, with cumulative progress explicitly labeled in the UI. Independent exam banks and the final unseen multi-table assessment are Planned. Four projects provide briefs, synthetic data, analysis questions and self-review rubrics; they are not automatically marked complete or scored. The final e-commerce brief asks for cleaning, joins, metrics, charts and five evidence-based findings.

## Expansion acceptance criteria

Prioritize the complete beginner sequence (types, strings, conditions, loops, collections, functions, errors, files) before increasing statistical complexity. Add worked examples with expected reasoning, common mistakes, varied data contracts, general-solution tests and sample-hardcoding rejection. Then deepen NumPy/pandas, merge cardinality, EDA, visual interpretation, probability, SciPy and A/B assumptions, SQL joins, Excel and API ingestion. External API practice must use fixtures or a separate reviewed network boundary, not internet access in learner containers.

The v1 threshold is at least 40 reviewed lessons, 200 varied questions, 70 practical challenges, 7 independent exams, 4 assessed projects and a real final assessment. Counts alone are insufficient. Content must be solvable from taught prerequisites, produce meaningful feedback, and pass technical and educational review.
