from backend.src.enums.user_role import UserRole


# Users

admin_user_create = {
    "name": "Admin",
    "email": "admin@example.com",
    "password": "Admin123!",
    "role": UserRole.HR,
    "admin": True,
}

managing_director_create =  {
    "name": "Jack Sim", 
    "email": "jack.sim@kira.ai", 
    "password": "Password123!", 
    "role": UserRole.DIRECTOR,
    "admin": True
}