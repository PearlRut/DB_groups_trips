# דוח הפרויקט שלב ג' - אינטגרציה ומבטים

דוח זה מציג את תהליך האינטגרציה הפיזי והלוגי שבוצע בין מערכת ניהול הטיולים הקבוצתיים של קבוצתנו לבין מערכת הלוגיסטיקה ואספקת הטיולים של הקבוצה שקיבלנו. הדוח מפרט את הדיאגרמות, החלטות העיצוב, אלגוריתם ההינדוס לאחור, יצירת המבטים והשאילתות עליהם, וכן את קובץ הגיבוי הסופי להגשה.

---

## 1. תרשימי ה-ERD וה-DSD של שתי המערכות

האינטגרציה התבססה על ניתוח מעמיק של המבנה המקורי של שתי המערכות:

### א. תרשימי המערכת שקיבלנו (האגף הלוגיסטי)
* **ERD אגף חדש (שקיבלנו):** [forintegration.erdplus](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/forintegration.erdplus)
* **DSD אגף חדש (שקיבלנו):**
  ![DSD אגף חדש](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/dsdForIntefration.png)

### ב. תרשימי המערכת המאוחדת והמשותפת לאחר האינטגרציה
* **ERD משותף ומאוחד:** [unified_erd.erdplus](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/unified_erd.erdplus)
* **DSD לאחר אינטגרציה:** [unified_erd-Relational Schema.erdplus](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/unified_erd-Relational Schema.erdplus)

### ג. גלריית צילומי מסך מהעיצוב ב-ERDPlus (מתיקיית img):
* **תרשים 1 - שחזור מערכת הלוגיסטיקה:**  
  ![צילום מסך 1](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/img/צילום%20מסך%202026-05-13%20ב-14.23.04.png)
* **תרשים 2 - מפתחות וקשרים ראשוניים:**  
  ![צילום מסך 2](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/img/צילום%20מסך%202026-05-13%20ב-14.30.32.png)
* **תרשים 3 - אינטגרציה סופית:**  
  ![צילום מסך 3](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/img/צילום%20מסך%202026-05-13%20ב-14.37.03.png)

---

## 2. אלגוריתם הינדוס לאחור (Reverse Engineering Algorithm)

לצורך הבנת מבנה המערכת שקיבלנו ללא תיעוד מקורי, יישמנו **אלגוריתם הינדוס לאחור** (Reverse Engineering) המאפשר שחזור של תרשים ERD קונספטואלי מתוך הסכימה הלוגית (הטבלאות ב-DSD ומפתחות זרים). 

### שלבי האלגוריתם:

1. **זיהוי ישויות חזקות (Strong Entities):**
   * **כלל:** כל טבלה שיש לה מפתח ראשי (Primary Key) יחיד שאינו מפתח זר (Foreign Key) המצביע לטבלה אחרת, ממופה ל**ישות רגילה** (Entity) בתרשים ה-ERD.
   * **דוגמה מהלוגיסטיקה:** הטבלאות `supplier` (עם מפתח `supplierid`), `equipment` (`equipmentid`) ו-`location` (`locationid`) זוהו כישויות עצמאיות חזקות.

2. **זיהוי ישויות חלשות (Weak Entities):**
   * **כלל:** טבלה שהמפתח הראשי שלה מורכב ממפתח זר המצביע לישות אחרת בתוספת מפתח חלקי (Discriminator), ממופה ל**ישות חלשה** (Weak Entity).
   * **דוגמה אצלנו:** טבלת `schedules` שהמפתח שלה מורכב מ-`trip_id` (מפתח זר) ו-`order_num`.

3. **זיהוי קשרי יחיד-לרבים (1:N Relationships):**
   * **כלל:** לכל מפתח זר (FK) בטבלה A שמצביע למפתח ראשי בטבלה B (כאשר המפתח הזר אינו חלק מהמפתח הראשי של טבלה A), ניצור קשר מסוג 1:N בין ישות B לישות A.
   * **ערכיות (Optionality):** אם עמודת המפתח הזר מאפשרת ערכי `NULL`, הקשר הוא אופציונלי בצד של A. אם מוגדר `NOT NULL`, הקשר הוא חובה.
   * **דוגמה מהלוגיסטיקה:** בטבלת `equipment` קיים מפתח זר `supplierid` המפנה ל-`supplier`. לכן נוצר קשר 1:N שבו ספק אחד מספק פריטי ציוד רבים.

4. **זיהוי קשרי רבים-לרבים (M:N Relationships):**
   * **כלל:** כל טבלת גישור (Junction Table) שהמפתח הראשי שלה הוא מפתח מורכב (Composite PK) המורכב משני מפתחות זרים או יותר המצביעים לטבלאות שונות, תתורגם בתרשים ה-ERD ל**קשר M:N** ישיר בין אותן ישויות. עמודות נוספות בטבלת הגישור (שאינן מפתחות) יהפכו לתכונות של הקשר (Relationship Attributes).
   * **דוגמה מהלוגיסטיקה:** טבלת הגישור `trip_equipment` עם מפתח מורכב `(tripid, equipmentid)` תורגמה לקשר M:N בין הטיול לציוד, והעמודה `quantityallocated` הפכה לתכונה של הקשר.

5. **זיהוי ירושה ותת-טיפוסים (Subtypes/Supertypes):**
   * **כלל:** קשר של 1:1 בין מפתחות ראשיים של שתי טבלאות (כאשר המפתח הראשי של טבלה A הוא גם מפתח זר המפנה למפתח הראשי של טבלה B) ממופה לקשר של **הכללה/ירושה** (Subtype/Supertype).
   * **דוגמה אצלנו:** טבלת `guides` שחולקת מפתח ראשי `participant_id` עם טבלת `participants`.

---

## 3. החלטות עיצוביות בשלב האינטגרציה

במהלך עיצוב ה-ERD המשולב, קיבלנו מספר החלטות אסטרטגיות כדי להבטיח את תקינות המאגר ומניעת כפילויות:

* **החלטה 1: בחירת ישות הטיול המרכזית:** החלטנו להשתמש בטבלת `trips` המקורית של קבוצתנו כגרעין המרכזי של הטיולים, שכן היא מחוברת ללו"ז הטיול ולמסלולים. הוספנו לטבלה זו את השדה `trip_type` שהיה קיים אצלם, וביצענו מיזוג של הנתונים הקיימים.
* **החלטה 2: נרמול טבלת התחבורה (3NF):** במקור, הקבוצה השנייה שמרה את סוג הרכב כטקסט חופשי (`vehicle_type`) בטבלת `transportation`. כדי לשמור על תקינות ונרמול, קישרנו את הרכבים שלהם ישירות לטבלת הקטלוג של סוגי התחבורה שלנו (`transport_types`) באמצעות מפתח זר, והוספנו את הסוג החדש `'Minibus'` לקטלוג המשותף.
* **החלטה 3: איחוד משתתפים ורישום:** טבלאות המטיילים והרישום שלהם (`participant` ו-`registers_to`) נמחקו ובמקומן השתמשנו בתשתיות העשירות שלנו (`participants` ו-`trip_participants`), המכילות גם ניהול סגל מדריכים ואישורי הגעה.
* **החלטה 4: הסבת מפתחות זרים לטיולים:** כל קשרי הלוגיסטיקה של הקבוצה השנייה (`location_trip`, `trip_equipment`, `trip_transportation`) עודכנו כך שמזהה הטיול שונה מ-`tripid` ל-`trip_id` כדי להתאים לקונבנציה שלנו, והמפתחות הזרים הופנו לטבלת הליבה המאוחדת `trips`.

---

## 4. הסבר מילולי של התהליך והפקודות (אינטגרציה פיזית)

האינטגרציה הפיזית בוצעה בהצלחה באמצעות הרצת קובץ ה-SQL המשולב [integrate.sql](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/integrate.sql) המבצע את הפעולות הבאות:
1. **שינוי מבנה `trips` והעתקת נתונים:** הוספת עמודה `trip_type`, הרצת שאילתת `UPDATE` המעתיקה את סוגי הטיול מהטבלה שלהם לפי מזהה תואם, והחלת אילוץ `NOT NULL`.
2. **ניתוב מפתחות זרים בלוגיסטיקה:** מחיקת המפתחות הזרים הישנים שהצביעו לטבלה שלהם, שינוי שם העמודה ל-`trip_id` והוספת מפתח זר חדש המקשר ל-`trips(trip_id)` עם תמיכה במחיקה מדורגת (`ON DELETE CASCADE`).
3. **נרמול רכבים מול קטלוג התחבורה:** הוספת `'Minibus'` לקטלוג `transport_types`, יצירת עמודת מפתח זר `transport_type_id` בטבלת `transportation`, הרצת שאילתת תרגום המקשרת כל רכב ל-ID המתאים לפי סוג הרכב הטקסטואלי שהיה להם, ולבסוף מחיקת עמודת הטקסט המקורית `vehicle_type`.
4. **ניקוי טבלאות כפולות:** הרצת פקודות `DROP TABLE` לניקוי הטבלאות הישנות והכפולות שלהם (`registers_to`, `participant`, `trip`).

---

## 5. תיעוד מפורט של המבטים (Views) והשאילתות על המבטים

כל פקודות היצירה והשאילתות שמורות בקובץ הרשמי [Views.sql](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/Views.sql). להלן התיעוד המלא שלהם:

### א. מבט 1 (מנקודת המבט של האגף שלנו - ניהול טיולים)

#### תיאור מילולי:
מבט מקיף המיועד למנהלי הטיולים. הוא מחבר בין נתוני הטיול, המסלול המשויך אליו, סוג התחבורה הכללי המבוקש, ומבצע חישובי צבירה לקבלת כמות המשתתפים הרשומים בפועל, מקומות פנויים ואחוז תפוסה נוכחי בכל טיול.

#### קוד יצירת המבט:
```sql
CREATE OR REPLACE VIEW public.trip_planning_summary_view AS
SELECT
    t.trip_id,
    t.trip_name,
    t.trip_type,
    r.route_name,
    r.region,
    r.difficulty_level,
    t.start_date,
    t.end_date,
    t.group_size,
    COUNT(tp.participant_id) AS registered_participants,
    t.group_size - COUNT(tp.participant_id) AS available_places,
    ROUND((COUNT(tp.participant_id)::numeric / NULLIF(t.group_size, 0)) * 100, 2) AS occupancy_percentage,
    t.status
FROM public.trips t
JOIN public.routes r ON t.route_id = r.route_id
LEFT JOIN public.trip_participants tp ON t.trip_id = tp.trip_id
GROUP BY
    t.trip_id,
    t.trip_name,
    t.trip_type,
    r.route_name,
    r.region,
    r.difficulty_level,
    t.start_date,
    t.end_date,
    t.group_size,
    t.status;
```

#### פלט שליפת נתונים מהמבט (`SELECT * LIMIT 10`):
```
 trip_id |   trip_name    | trip_type |  route_name   |  region   | difficulty_level | start_date |  end_date  | group_size | registered_participants | available_places | occupancy_percentage | status  
---------+----------------+-----------+---------------+-----------+------------------+------------+------------+------------+-------------------------+------------------+----------------------+---------
       1 | Spring Trip    | City      | Desert Trail  | South     | Medium           | 2026-04-01 | 2026-04-03 |         20 |                      40 |              -20 |               200.00 | Planned
       2 | Adventure Trip | City      | Mountain Path | North     | Hard             | 2026-05-10 | 2026-05-12 |         10 |                      30 |              -20 |               300.00 | Open
       3 | Trip_1         | Nature    | Route_219     | North     | Medium           | 2026-07-14 | 2026-07-19 |         22 |                      39 |              -17 |               177.27 | Closed
       4 | Trip_2         | Extreme   | Route_188     | North     | Easy             | 2027-11-24 | 2027-11-30 |          7 |                      46 |              -39 |               657.14 | Open
       5 | Trip_3         | Extreme   | Route_36      | North     | Easy             | 2027-06-16 | 2027-06-22 |         32 |                      36 |               -4 |               112.50 | Planned
       6 | Trip_4         | Extreme   | Route_274     | Jerusalem | Medium           | 2027-05-04 | 2027-05-07 |          8 |                      43 |              -35 |               537.50 | Closed
       7 | Trip_5         | Nature    | Route_354     | South     | Hard             | 2026-03-10 | 2026-03-13 |         16 |                      40 |              -24 |               250.00 | Open
       8 | Trip_6         | Extreme   | Route_472     | South     | Hard             | 2027-01-06 | 2027-01-08 |         39 |                      40 |               -1 |               102.56 | Active
       9 | Trip_7         | Extreme   | Route_492     | Center    | Easy             | 2025-08-24 | 2025-08-30 |         38 |                      32 |                6 |                84.21 | Planned
      10 | Trip_8         | City      | Route_25      | Coastal   | Easy             | 2026-05-20 | 2026-05-21 |         21 |                      46 |              -25 |               219.05 | Open
```

---

### ב. שאילתות על מבט 1

#### 🔍 שאילתה 1.1: שליפת טיולים מאתגרים בעלי תפוסה גבוהה
* **תיאור מילולי:** מציאת כל הטיולים המשויכים למסלול קשה ('Hard') בעלי אחוז תפוסה השווה או גדול מ-75%, ממוינים לפי התפוסה הגבוהה ביותר. השאילתה מסייעת לזהות ביקוש גבוה לטיולים מאתגרים.
* **קוד השאילתה:**
  ```sql
  SELECT 
      trip_id,
      trip_name,
      route_name,
      difficulty_level,
      group_size,
      registered_participants,
      occupancy_percentage,
      status
  FROM public.trip_planning_summary_view
  WHERE LOWER(difficulty_level) = 'hard'
    AND occupancy_percentage >= 75.00
  ORDER BY occupancy_percentage DESC;
  ```
* **פלט הרצה (10 שורות ראשונות):**
  ```
   trip_id | trip_name | route_name | difficulty_level | group_size | registered_participants | occupancy_percentage | status  
  ---------+-----------+------------+------------------+------------+-------------------------+----------------------+---------
       103 | Trip_101  | Route_368  | Hard             |          6 |                      48 |               800.00 | Planned
       333 | Trip_331  | Route_35   | Hard             |          5 |                      40 |               800.00 | Planned
       364 | Trip_362  | Route_351  | Hard             |          5 |                      40 |               800.00 | Closed
       203 | Trip_201  | Route_373  | Hard             |          7 |                      48 |               685.71 | Closed
       323 | Trip_321  | Route_270  | Hard             |          8 |                      53 |               662.50 | Closed
        56 | Trip_54   | Route_134  | Hard             |          7 |                      41 |               585.71 | Active
       187 | Trip_185  | Route_137  | Hard             |          8 |                      46 |               575.00 | Active
       319 | Trip_317  | Route_485  | Hard             |          6 |                      33 |               550.00 | Open
       359 | Trip_357  | Route_78   | Hard             |          7 |                      38 |               542.86 | Planned
       138 | Trip_136  | Route_253  | Hard             |          8 |                      39 |               487.50 | Active
  ```

#### 🔍 שאילתה 1.2: סטטיסטיקת תכנון חודשית ואזורית
* **תיאור מילולי:** חישוב סטטיסטיקה חודשית לכל אזור גיאוגרפי: מספר הטיולים המתוכננים, הקיבולת המקסימלית המתוכננת, כמות הנרשמים הכוללת ומספר המקומות הפנויים/החסרים באותו חודש.
* **קוד השאילתה:**
  ```sql
  SELECT 
      region,
      EXTRACT(YEAR FROM start_date) AS plan_year,
      EXTRACT(MONTH FROM start_date) AS plan_month,
      COUNT(trip_id) AS total_trips,
      SUM(group_size) AS total_max_capacity,
      SUM(registered_participants) AS total_registrations,
      SUM(available_places) AS total_empty_seats
  FROM public.trip_planning_summary_view
  GROUP BY 
      region, 
      EXTRACT(YEAR FROM start_date), 
      EXTRACT(MONTH FROM start_date)
  ORDER BY plan_year, plan_month, total_trips DESC;
  ```
* **פלט הרצה (10 שורות ראשונות):**
  ```
    region   | plan_year | plan_month | total_trips | total_max_capacity | total_registrations | total_empty_seats 
  -----------+-----------+------------+-------------+--------------------+---------------------+-------------------
   North     |      2025 |          1 |           4 |                103 |                 151 |               -48
   Jerusalem |      2025 |          1 |           4 |                 54 |                 136 |               -82
   Coastal   |      2025 |          1 |           3 |                 54 |                 127 |               -73
   Center    |      2025 |          1 |           2 |                 65 |                  68 |                -3
   South     |      2025 |          1 |           1 |                 15 |                  50 |               -35
   Center    |      2025 |          2 |           3 |                102 |                 126 |               -24
   Coastal   |      2025 |          2 |           2 |                 55 |                  91 |               -36
   Jerusalem |      2025 |          2 |           2 |                 92 |                  80 |                12
   South     |      2025 |          2 |           1 |                 14 |                  29 |               -15
   North     |      2025 |          2 |           1 |                 39 |                  54 |               -15
  ```

---

### ג. מבט 2 (מנקודת המבט של האגף הלוגיסטי - תפעול וספקים)

#### תיאור מילולי:
מבט מורכב ומאוחד המציג את תפעול הלוגיסטיקה עבור כל טיול. הוא מחבר בין הטיול לבין הרכבים הפיזיים המשויכים אליו (מספרי רכב, קיבולת, שם ספק התחבורה), הציוד הלוגיסטי שהוקצה לו (פריטי הציוד, כמויות, ושם ספק הציוד) והנקודות הגיאוגרפיות (Locations) שבהן הטיול עובר.

#### קוד יצירת המבט:
```sql
CREATE OR REPLACE VIEW public.trip_logistics_operations_view AS
SELECT
    t.trip_id,
    t.trip_name,
    t.trip_type,
    t.start_date,
    -- Transportation details
    tr.transportid AS specific_vehicle_id,
    tt.transport_type_name AS vehicle_category,
    tr.capacity AS vehicle_capacity,
    s_trans.company_name AS transport_supplier,
    -- Equipment details
    eq.equipmentid,
    eq.itemname AS equipment_name,
    te.quantityallocated AS equipment_quantity,
    s_eq.company_name AS equipment_supplier,
    -- Location details
    loc.locationid,
    loc.locationname,
    loc.region AS location_region,
    loc.address AS location_address
FROM public.trips t
LEFT JOIN public.trip_transportation tt_map ON t.trip_id = tt_map.trip_id
LEFT JOIN public.transportation tr ON tt_map.transportid = tr.transportid
LEFT JOIN public.transport_types tt ON tr.transport_type_id = tt.transport_type_id
LEFT JOIN public.supplier s_trans ON tr.supplierid = s_trans.supplierid
LEFT JOIN public.trip_equipment te ON t.trip_id = te.trip_id
LEFT JOIN public.equipment eq ON te.equipmentid = eq.equipmentid
LEFT JOIN public.supplier s_eq ON eq.supplierid = s_eq.supplierid
LEFT JOIN public.location_trip lt ON t.trip_id = lt.trip_id
LEFT JOIN public.location loc ON lt.locationid = loc.locationid;
```

#### פלט שליפת נתונים מהמבט (`SELECT * LIMIT 10`):
```
 trip_id |  trip_name  | trip_type | start_date | specific_vehicle_id | vehicle_category | vehicle_capacity | transport_supplier | equipmentid | equipment_name | equipment_quantity | equipment_supplier | locationid | locationname | location_region | location_address 
---------+-------------+-----------+------------+---------------------+------------------+------------------+--------------------+-------------+----------------+--------------------+--------------------+------------+--------------+-----------------+------------------
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |          3 | PyLoc 3      | North           | PyStreet 3
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         20 | PyLoc 20     | Center          | PyStreet 20
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         27 | PyLoc 27     | North           | PyStreet 27
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         34 | PyLoc 34     | South           | PyStreet 34
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         37 | PyLoc 37     | North           | PyStreet 37
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         43 | PyLoc 43     | South           | PyStreet 43
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         72 | PyLoc 72     | Center          | PyStreet 72
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         77 | PyLoc 77     | South           | PyStreet 77
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |         95 | PyLoc 95     | North           | PyStreet 95
       1 | Spring Trip | City      | 2026-04-01 |                   6 | Bus              |               50 | PySupplier 328     |         348 | PyGear 348     |                  2 | PySupplier 236     |        108 | PyLoc 108    | South           | PyStreet 108
```

---

### ד. שאילתות על מבט 2

#### 🔍 שאילתה 2.1: עומס הקצאות ולוגיסטיקה על פי ספק
* **תיאור מילולי:** חישוב סטטיסטיקת ההעמסה על כל חברות הספקים המשולבות (ספקי תחבורה וציוד): כמות כלי הרכב ששוריינו מכל ספק, סך כמויות פריטי הציוד שהוקצו, ומספר הטיולים הפעילים הנתמכים על ידי כל חברה.
* **קוד השאילתה:**
  ```sql
  SELECT 
      COALESCE(transport_supplier, equipment_supplier) AS supplier_company,
      COUNT(DISTINCT specific_vehicle_id) AS total_vehicles_booked,
      COALESCE(SUM(equipment_quantity), 0) AS total_equipment_items_allocated,
      COUNT(DISTINCT trip_id) AS active_trips_supported
  FROM public.trip_logistics_operations_view
  WHERE transport_supplier IS NOT NULL OR equipment_supplier IS NOT NULL
  GROUP BY COALESCE(transport_supplier, equipment_supplier)
  ORDER BY total_equipment_items_allocated DESC, total_vehicles_booked DESC;
  ```
* **פלט הרצה (10 שורות ראשונות):**
  ```
   supplier_company | total_vehicles_booked | total_equipment_items_allocated | active_trips_supported 
  ------------------+-----------------------+---------------------------------+------------------------
   PySupplier 183   |                     4 |                            1000 |                      8
   PySupplier 215   |                     3 |                            1000 |                      5
   PySupplier 179   |                     2 |                            1000 |                      5
   PySupplier 228   |                     3 |                             900 |                      8
   PySupplier 40    |                     2 |                             800 |                      6
   PySupplier 231   |                     2 |                             800 |                      4
   PySupplier 267   |                     1 |                             800 |                      5
   PySupplier 115   |                     4 |                             700 |                      6
   PySupplier 209   |                     3 |                             700 |                      7
   PySupplier 344   |                     1 |                             700 |                      7
  ```

#### 🔍 שאילתה 2.2: בדיקת תפוסת רכבים באזור הדרום לטיולים גדולים
* **תיאור מילולי:** איתור כל הטיולים העוברים בנקודות עניין באזור הדרום ('South') ושוריין עבורם כלי רכב גדול (קיבולת גדולה מ-15 מקומות), על מנת לבצע בקרת בטיחות ותיאום נהגים.
* **קוד השאילתה:**
  ```sql
  SELECT DISTINCT
      trip_id,
      trip_name,
      location_region,
      locationname,
      vehicle_category,
      vehicle_capacity,
      transport_supplier
  FROM public.trip_logistics_operations_view
  WHERE location_region = 'South'
    AND vehicle_capacity > 15
  ORDER BY vehicle_capacity DESC, trip_name;
  ```
* **פלט הרצה (10 שורות ראשונות):**
  ```
   trip_id | trip_name | location_region | locationname | vehicle_category | vehicle_capacity | transport_supplier 
  ---------+-----------+-----------------+--------------+------------------+------------------+--------------------
         3 | Trip_1    | South           | PyLoc 308    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 350    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 490    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 463    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 161    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 75     | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 331    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 218    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 170    | Jeep             |               55 | PySupplier 438
         3 | Trip_1    | South           | PyLoc 332    | Jeep             |               55 | PySupplier 438
  ```

---

## 6. אימות תאימות לאחור (שאילתות שלב ב')

כדי לוודא שתהליך המיזוג לא גרם לתופעות לוואי במבנה הקיים, הרצנו את כל קובץ השאילתות משלב ב' ([Queries.sql](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_B/Queries.sql)) על מסד הנתונים המשולב `unified_db`. 

**תוצאת הבדיקה:**  
ההרצה עברה בהצלחה מלאה עם **0 שגיאות**! כל הטבלאות המקוריות (`trips`, `routes`, `participants`, `schedules`, `events`, `actions`, `trip_participants`, `guides`, `transport_types`) שמרו על שמותיהן, עמודותיהן והמפתחות שלהן, מה שמבטיח תאימות לאחור מלאה לכל מסכי המערכת שפותחו בשלבים הקודמים.

---

## 7. קובץ גיבוי להגשה - backup3

גיבוי מלא של בסיס הנתונים המשולב, הכולל את כל הטבלאות המקוריות והחדשות, הנתונים המלאים, המפתחות הזרים, האינדקסים ושני המבטים שיצרנו, נשמר בפורמט SQL נייד ותקני בקובץ:
👉 **[backup3](file:///Users/ruthgold/Desktop/DB/DB_group_trips/Phase_C/backup3)** (גודל קובץ: כ-1.82MB).
