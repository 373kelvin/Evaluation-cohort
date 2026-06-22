# Artifact Inventory — College-ERP-master

**Summary:** 90 artifacts (class: 54, function: 32, model: 2, test: 2)

## Classs

| Name | Source | Detail |
|------|--------|--------|
| `ApisConfig` | `apis/apps.py:4` | Python class |
| `AttendanceSerializer` | `apis/serializers.py:12` | Python class |
| `MarksSerializer` | `apis/serializers.py:18` | Python class |
| `TimeTableSerializer` | `apis/serializers.py:24` | Python class |
| `DetailSerializer` | `apis/serializers.py:6` | Python class |
| `TimetableView` | `apis/views.py:116` | Python class |
| `DetailView` | `apis/views.py:21` | Python class |
| `AttendanceView` | `apis/views.py:46` | Python class |
| `MarksView` | `apis/views.py:83` | Python class |
| `ClassInline` | `info/admin.py:28` | Python class |
| `DeptAdmin` | `info/admin.py:33` | Python class |
| `StudentInline` | `info/admin.py:40` | Python class |
| `ClassAdmin` | `info/admin.py:45` | Python class |
| `CourseAdmin` | `info/admin.py:52` | Python class |
| `AssignTimeInline` | `info/admin.py:58` | Python class |
| `AssignAdmin` | `info/admin.py:63` | Python class |
| `MarksInline` | `info/admin.py:71` | Python class |
| `StudentCourseAdmin` | `info/admin.py:76` | Python class |
| `StudentAdmin` | `info/admin.py:83` | Python class |
| `TeacherAdmin` | `info/admin.py:89` | Python class |
| `AttendanceClassAdmin` | `info/admin.py:95` | Python class |
| `InfoConfig` | `info/apps.py:4` | Python class |
| `Migration` | `info/migrations/0001_initial.py:12` | Python class |
| `Migration` | `info/migrations/0002_auto_20181109_1947.py:6` | Python class |
| `Migration` | `info/migrations/0003_auto_20181109_2003.py:6` | Python class |
| `Migration` | `info/migrations/0004_auto_20181109_2013.py:6` | Python class |
| `Migration` | `info/migrations/0005_auto_20181109_2024.py:6` | Python class |
| `Migration` | `info/migrations/0006_teacher_user.py:8` | Python class |
| `Migration` | `info/migrations/0007_auto_20181109_2238.py:6` | Python class |
| `Migration` | `info/migrations/0008_auto_20181111_1107.py:6` | Python class |
| `Migration` | `info/migrations/0009_auto_20181111_1112.py:6` | Python class |
| `Migration` | `info/migrations/0010_auto_20181111_1218.py:6` | Python class |
| `Migration` | `info/migrations/0011_auto_20181111_2017.py:6` | Python class |
| `Migration` | `info/migrations/0012_auto_20181111_2018.py:6` | Python class |
| `Migration` | `info/migrations/0013_auto_20181112_1846.py:7` | Python class |
| `Migration` | `info/migrations/0014_auto_20201028_2022.py:6` | Python class |
| `Migration` | `info/migrations/0015_attendancerange.py:6` | Python class |
| `Migration` | `info/migrations/0016_auto_20210820_1553.py:6` | Python class |
| `Teacher` | `info/models.py:104` | Python class |
| `Assign` | `info/models.py:116` | Python class |
| `AssignTime` | `info/models.py:131` | Python class |
| `AttendanceClass` | `info/models.py:137` | Python class |
| `Attendance` | `info/models.py:147` | Python class |
| `AttendanceTotal` | `info/models.py:160` | Python class |
| `StudentCourse` | `info/models.py:205` | Python class |
| `Marks` | `info/models.py:231` | Python class |
| `MarksClass` | `info/models.py:246` | Python class |
| `AttendanceRange` | `info/models.py:261` | Python class |
| `User` | `info/models.py:45` | Python class |
| `Dept` | `info/models.py:59` | Python class |
| `Course` | `info/models.py:67` | Python class |
| `Class` | `info/models.py:77` | Python class |
| `Student` | `info/models.py:92` | Python class |
| `InfoTest` | `info/tests.py:10` | Python class |

## Functions

| Name | Source | Detail |
|------|--------|--------|
| `daterange` | `info/admin.py:23` | Python function |
| `daterange` | `info/models.py:269` | Python function |
| `create_attendance` | `info/models.py:284` | Python function |
| `create_marks` | `info/models.py:297` | Python function |
| `create_marks_class` | `info/models.py:330` | Python function |
| `delete_marks` | `info/models.py:340` | Python function |
| `edit_att` | `info/views.py:102` | Python function |
| `confirm` | `info/views.py:114` | Python function |
| `t_attendance_detail` | `info/views.py:143` | Python function |
| `change_att` | `info/views.py:151` | Python function |
| `t_extra_class` | `info/views.py:159` | Python function |
| `index` | `info/views.py:17` | Python function |
| `e_confirm` | `info/views.py:170` | Python function |
| `t_report` | `info/views.py:191` | Python function |
| `timetable` | `info/views.py:201` | Python function |
| `t_timetable` | `info/views.py:225` | Python function |
| `free_teachers` | `info/views.py:250` | Python function |
| `marks_list` | `info/views.py:266` | Python function |
| `attendance` | `info/views.py:28` | Python function |
| `t_marks_list` | `info/views.py:291` | Python function |
| `t_marks_entry` | `info/views.py:298` | Python function |
| `marks_confirm` | `info/views.py:311` | Python function |
| `edit_marks` | `info/views.py:329` | Python function |
| `student_marks` | `info/views.py:346` | Python function |
| `add_teacher` | `info/views.py:353` | Python function |
| `add_student` | `info/views.py:390` | Python function |
| `attendance_detail` | `info/views.py:43` | Python function |
| `t_clas` | `info/views.py:53` | Python function |
| `t_student` | `info/views.py:59` | Python function |
| `t_class_date` | `info/views.py:73` | Python function |
| `cancel_class` | `info/views.py:81` | Python function |
| `t_attendance` | `info/views.py:89` | Python function |

## Models

| Name | Source | Detail |
|------|--------|--------|
| `models.py` | `apis/models.py` | data model / schema |
| `models.py` | `info/models.py` | data model / schema |

## Tests

| Name | Source | Detail |
|------|--------|--------|
| `tests.py` | `apis/tests.py` | test file |
| `tests.py` | `info/tests.py` | test file |
