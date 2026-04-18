from django.urls import path, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ==========================================
# 1. AUTHENTICATION & LOGIN MOCKS
# ==========================================
@csrf_exempt
def mock_challenge(request, *args, **kwargs):
    return JsonResponse({
        "message": "Challenge generated successfully.",
        "challenge": "a1b2c3d4e5f6g7h8i9j0"
    }, status=200)

@csrf_exempt
def mock_login(request, *args, **kwargs):
    return JsonResponse({
        "access": "fake_access_token",
        "refresh": "fake_refresh_token",
        "device_status": "SECURE"
    }, status=200)

# ==========================================
# 2. PROFILE & CLASSROOM MOCKS (Unified for Teacher & Student)
# ==========================================
@csrf_exempt
def mock_profile(request, *args, **kwargs):
    # Includes both student and teacher fields so it works for either login
    return JsonResponse({
        "id": 1,
        "username": "Reviewer",
        "uid": "2023800010", 
        "branch": "CSE",
        "department": "CSE",
        "fcm_token": "dummy_token",
        "public_key": "dummy_key"
    }, status=200)

@csrf_exempt
def mock_classrooms(request, *args, **kwargs):
    return JsonResponse([{
        "id": 1,
        "name": "Testing Classroom 1",
        "code": "CLASS101",
        "teacher_name": "Teacher Reviewer",
        "created_at": "2026-04-18T10:00:00Z",
        "active": True
    }], safe=False, status=200)

@csrf_exempt
def mock_attendance_list(request, *args, **kwargs):
    return JsonResponse([{
        "id": 1,
        "student": 1,
        "classroom": 1,
        "date": "2026-04-18",
        "status": "PRESENT",
        "timestamp": "2026-04-18T10:00:00Z"
    }], safe=False, status=200)

# ==========================================
# 3. ATTENDANCE SESSION & BLE MESH MOCKS
# ==========================================
@csrf_exempt
def mock_session_status(request, *args, **kwargs):
    return JsonResponse({
        "active": True, 
        "message": "Attendance session is active"
    }, status=200)

@csrf_exempt
def mock_active_sessions_list(request, *args, **kwargs):
    # Explicitly tells the Teacher App that Classroom ID 1 is currently LIVE
    return JsonResponse({"active_sessions": [1]}, status=200)

@csrf_exempt
def mock_session_credentials(request, *args, **kwargs):
    # Works for both teacher and student credential fetching
    return JsonResponse({
        "k_class": "1234567890abcdef1234567890abcdef",
        "session_seed": "abcdef1234567890abcdef1234567890",
        "node_id": 1
    }, status=200)

@csrf_exempt
def mock_teacher_gps(request, *args, **kwargs):
    return JsonResponse({"latitude": 19.0760, "longitude": 72.8777}, status=200)

# ==========================================
# 4. ADMIN TELEMETRY / GRAPH MOCK
# Gives the Teacher/Admin UI a fake connected graph to display
# ==========================================
@csrf_exempt
def mock_admin_state(request, *args, **kwargs):
    return JsonResponse({
        "active": True,
        "telemetry": {
            "total_enrolled": 1,
            "total_connected": 1,
            "orphaned": 0,
            "master_nodes_count": 0,
            "pending_exceptions": 0
        },
        "graph": {
            "nodes": [
                {"id": "teacher_001", "label": "Teacher", "type": "teacher", "is_exception": False, "is_marked": False},
                {"id": "student_001", "label": "Student Tester", "type": "student", "is_exception": False, "is_marked": False}
            ],
            "edges": [
                {"id": "edge_t1_s1", "source": "teacher_001", "target": "student_001"}
            ]
        }
    }, status=200)

# ==========================================
# 5. SMART CATCH-ALL
# ==========================================
@csrf_exempt
def generic_success(request, *args, **kwargs):
    path_req = request.path.lower()
    
    # If the app asks ANY unmapped URL if a session is active, say YES.
    if 'status' in path_req or 'session' in path_req:
        return JsonResponse({"active": True, "active_sessions": [1]}, status=200)
    
    # If it's a GET request, return empty array to prevent Flutter List crashes
    if request.method == 'GET':
        return JsonResponse([], safe=False, status=200)
    
    return JsonResponse({"status": "success", "message": "Operation completed."}, status=200)

@csrf_exempt
def base_url_response(request, *args, **kwargs):
    return JsonResponse({"message": "Mock Backend is running!"})


# ==========================================
# URL ROUTING
# ==========================================
urlpatterns = [
    path('', base_url_response),

    # --- AUTH & PROFILE ---
    re_path(r'^user/login/?$', mock_login),
    re_path(r'^user/(student|teacher)/login/verify/?$', mock_login),
    re_path(r'^user/student/login/challenge/?$', mock_challenge),
    re_path(r'^user/register/(student|teacher)/?$', mock_login), 
    re_path(r'^user/profile/?$', mock_profile),
    
    # --- CLASSROOMS (Student & Teacher) ---
    re_path(r'^user/student/enrollments/?$', mock_classrooms),
    re_path(r'^user/student/classrooms/?$', mock_classrooms),
    re_path(r'^user/student/search-classroom/?$', mock_classrooms),
    re_path(r'^user/teacher/classrooms/?$', mock_classrooms), # <-- Fixed for Teacher!
    re_path(r'^user/student/attendance/?$', mock_attendance_list),
    
    # --- BLE SESSION STATUS ---
    re_path(r'^session/teacher/sessions/active/?$', mock_active_sessions_list), # <-- Fixed for Teacher!
    re_path(r'^session/status/\d+/?$', mock_session_status),
    re_path(r'^session/student/classroom/\d+/session/?$', mock_session_status),
    
    # --- SESSION CREDENTIALS & GPS ---
    re_path(r'^session/classroom/\d+/credentials/?$', mock_session_credentials),
    re_path(r'^session/teacher/classroom/\d+/credentials/?$', mock_session_credentials),
    re_path(r'^session/classroom/\d+/(student|teacher)/gps/?$', mock_teacher_gps),
    
    # --- ADMIN GRAPH / TELEMETRY ---
    re_path(r'^session/admin/session/\d+/state/?$', mock_admin_state), # <-- Beautiful Graph for Teacher!
    
    # --- THE CATCH-ALL ---
    re_path(r'^.*$', generic_success),
]