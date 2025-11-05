from datetime import date, datetime, timedelta
from backend.src.database.db_setup import SessionLocal
from backend.src.handlers import user_handler, task_handler, task_assignment_handler, comment_handler, department_handler, project_handler, report_handler
from backend.src.enums.user_role import UserRole
from backend.src.enums.task_status import TaskStatus
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def seed_database():
    """Seed the database with demo data."""

    # Create Root Admin User
    admin_user_create = {
        "name": "Root Admin",
        "email": "admin@kira.ai",
        "password": "Admin123!",
        "role": UserRole.HR,
        "admin": True,
    }
    admin = user_handler.create_user(**admin_user_create)
    print(f"\nCreated admin user: \n{admin.user_id}: {admin.name}, {admin.email}")
    print("\n" + "=" * 60)

    managing_director_create =  {
        "name": "Jack Sim",
        "email": "jack.sim@kira.ai",
        "password": "Password123!",
        "role": UserRole.DIRECTOR,
        "admin": True
    }

    managing_director = user_handler.create_user(**managing_director_create)
    print(f"\nCreated managing director user: \n{managing_director.user_id}: {managing_director.name}, {managing_director.email}")
    print("\n" + "=" * 60)

    # Create C-Suite Department and team
    c_suite_dept = department_handler.add_department(department_name="C-Suite", manager_id=managing_director.user_id, creator_id=admin.user_id)
    c_suite_team = department_handler.create_team_under_department(department_id=c_suite_dept['department_id'], team_name="C-Suite Team", manager_id=managing_director.user_id)

    print(f"\nCreated department: \n{c_suite_dept['department_id']}: {c_suite_dept['department_name']}, Manager ID: {c_suite_dept['manager_id']}")
    print("\n" + "=" * 60)

    # Create Directors
    directors_create = [
        {"name": "Derek Tan", "email": "derek.tan@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Ernst Sim", "email": "ernst.sim@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Eric Loh", "email": "eric.loh@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Philip Lee", "email": "philip.lee@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Sally Loh", "email": "sally.loh@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "David Yap", "email": "david.yap@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Peter Yap", "email": "peter.yap@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
    ]

    directors = []
    for director_data in directors_create:
        director = user_handler.create_user(**director_data)
        directors.append(director)
        department_handler.assign_user_to_team(team_id=c_suite_team['team_id'], user_id=director.user_id, manager_id=managing_director.user_id)
    
    print(f"\nCreated {len(directors)} director users.")
    for director in directors:
        print(f"{director.user_id}: {director.name}, {director.email}, {department_handler.view_department_by_id(director.department_id)['department_name']}, Assigned to Team: {c_suite_team['team_number']}")
    print("\n" + "=" * 60)


    # Create Departments
    departments_create = [
        {"name": "Sales Department", "manager_id": directors[0].user_id},
        {"name": "Consultancy Division Department", "manager_id": directors[1].user_id},
        {"name": "System Solutioning Division Department", "manager_id": directors[2].user_id},
        {"name": "Engineering Operation Division Department", "manager_id": directors[3].user_id},
        {"name": "HR and Admin Department", "manager_id": directors[4].user_id},
        {"name": "Finance Department", "manager_id": directors[5].user_id},
        {"name": "IT Department", "manager_id": directors[6].user_id},
    ]

    departments = []
    for dept_data in departments_create:
        dept = department_handler.add_department(department_name=dept_data["name"], manager_id=dept_data["manager_id"], creator_id=admin.user_id)
        departments.append(dept)

    print(f"\nCreated {len(departments)} departments.")
    for dept in departments:
        print(f"{dept['department_id']}: {dept['department_name']}, Manager: {user_handler.get_user(dept['manager_id']).name}")

    print("\n" + "=" * 60)

    # Create Department Teams
    teams_create = [
        {"team_name": "Sales Team", "manager_id": directors[0].user_id, "department_id": departments[0]['department_id']},
        {"team_name": "Consultancy Team", "manager_id": directors[1].user_id, "department_id": departments[1]['department_id']},
        {"team_name": "System Solutioning Team", "manager_id": directors[2].user_id, "department_id": departments[2]['department_id']},
        {"team_name": "Engineering Operation Team", "manager_id": directors[3].user_id, "department_id": departments[3]['department_id']},
        {"team_name": "HR and Admin Team", "manager_id": directors[4].user_id, "department_id": departments[4]['department_id']},
        {"team_name": "Finance Team", "manager_id": directors[5].user_id, "department_id": departments[5]['department_id']},
        {"team_name": "IT Team", "manager_id": directors[6].user_id, "department_id": departments[6]['department_id']},
    ]

    teams = []
    for team_data in teams_create:
        team = department_handler.create_team_under_department(**team_data)
        teams.append(team)
    
    print(f"\nCreated {len(teams)} teams under their respective departments.")
    for team in teams:
        print(f"{team['team_id']}: {team['team_name']}, Manager: {user_handler.get_user(team['manager_id']).name}, Team Number: {team['team_number']}")

    print("\n" + "=" * 60)

    # Sales Team Managers
    sales_users_create = [
        {"name": "Alice Tan", "email": "alice.tan@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Bob Lim", "email": "bob.lim@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Charlie Lee", "email": "charlie.lee@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Diana Ong", "email": "diana.ong@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Devi Vishwakumar", "email": "devi.vishwakumar@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
    ]

    sales_managers = []
    for user_data in sales_users_create:
        user = user_handler.create_user(**user_data)
        sales_managers.append(user)
        department_handler.assign_user_to_team(team_id=teams[0]['team_id'], user_id=user.user_id, manager_id=teams[0]['manager_id'])

    print(f"\nCreated {len(sales_users_create)} sales team managers.")
    for user in sales_managers:
        print(f"{user.user_id}: {user.name}, {user.email}, {department_handler.view_department_by_id(user.department_id)['department_name']}, Assigned to Team: {teams[0]['team_number']}")
    
    print("\n" + "=" * 60)

    # Create Account Teams under Sales Team
    account_teams_create = [
        {"team_name": "North Region Account Team", "manager_id": sales_managers[0].user_id},
        {"team_name": "South Region Account Team", "manager_id": sales_managers[1].user_id},
        {"team_name": "East Region Account Team", "manager_id": sales_managers[2].user_id},
        {"team_name": "West Region Account Team", "manager_id": sales_managers[3].user_id},
        {"team_name": "Central Region Account Team", "manager_id": sales_managers[4].user_id},
    ]

    account_teams = []
    for team_data in account_teams_create:
        team = department_handler.create_team_under_team(
            team_id=teams[0]['team_id'],
            team_name=team_data['team_name'],
            manager_id=team_data['manager_id']
        )
        account_teams.append(team)

    print(f"\nCreated {len(account_teams)} account teams under Sales department.")
    for team in account_teams:
        print(f"{team['team_id']}: {team['team_name']}, Manager: {user_handler.get_user(team['manager_id']).name}, Team Number: {team['team_number']}")
    
    # Create Account Managers under Sales Teams
    account_managers_create = [
        {"name": "Aisha Rahman", "email": "aisha.rahman@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Amarjit Singh", "email": "amarjit.singh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Angeline Lim", "email": "angeline.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Arun Nair", "email": "arun.nair@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Benjamin Lee", "email": "benjamin.lee@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Bryan Ong", "email": "bryan.ong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Cassandra Tay", "email": "cassandra.tay@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Cheryl Chan", "email": "cheryl.chan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Daniel Low", "email": "daniel.low@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Dinesh Pillai", "email": "dinesh.pillai@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Eddie Phua", "email": "eddie.phua@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Elaine Tan", "email": "elaine.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Farah Binte Ahmad", "email": "farah.ahmad@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Faizal Osman", "email": "faizal.osman@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Fiona Goh", "email": "fiona.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Gurpreet Kaur", "email": "gurpreet.kaur@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Hannah Chia", "email": "hannah.chia@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Harith Iskandar", "email": "harith.iskandar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Ian Foo", "email": "ian.foo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Irfan Yusof", "email": "irfan.yusof@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jacqueline Lim", "email": "jacqueline.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "James Pang", "email": "james.pang@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Janice Ho", "email": "janice.ho@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jasdeep Singh", "email": "jasdeep.singh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jennifer Tan", "email": "jennifer.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jeremy Ong", "email": "jeremy.ong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Joanne Lim", "email": "joanne.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Joseph Tan", "email": "joseph.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kavitha Raj", "email": "kavitha.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kelvin Chong", "email": "kelvin.chong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kenneth Chew", "email": "kenneth.chew@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kevin Ng", "email": "kevin.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Khairul Anwar", "email": "khairul.anwar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kimberly Teo", "email": "kimberly.teo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kiran Subramaniam", "email": "kiran.subramaniam@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Lakshmi Devi", "email": "lakshmi.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Lawrence Tan", "email": "lawrence.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Liyana Binte Noor", "email": "liyana.noor@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Maria Abdullah", "email": "maria.abdullah@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Mei Ling Tan", "email": "meiling.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Muthu Krishnan", "email": "muthu.krishnan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nadia Salleh", "email": "nadia.salleh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nirmala Devi", "email": "nirmala.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nurul Iman", "email": "nurul.iman@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Patrick Lim", "email": "patrick.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Pritam Kaur", "email": "pritam.kaur@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Rajesh Menon", "email": "rajesh.menon@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Ramesh Nair", "email": "ramesh.nair@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Roslan Bakar", "email": "roslan.bakar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Siti Nurhaliza", "email": "siti.nurhaliza@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Stephanie Wong", "email": "stephanie.wong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Suria Binte Ahmad", "email": "suria.ahmad@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Tan Wei Jie", "email": "tan.weijie@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Thomas Cheong", "email": "thomas.cheong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Umar Hakim", "email": "umar.hakim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Vanessa Tan", "email": "vanessa.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Wei Ming Goh", "email": "weiming.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Yasmin Ali", "email": "yasmin.ali@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Zulfiqar Hassan", "email": "zulfiqar.hassan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Zuraidah Binte Rahim", "email": "zuraidah.rahim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']}
    ]
    account_managers = []
    for user_data in account_managers_create:
        user = user_handler.create_user(**user_data)
        account_managers.append(user)
        department_handler.assign_user_to_team(
            team_id=account_teams[account_managers.index(user) % len(account_teams)]['team_id'],
            user_id=user.user_id,
            manager_id=account_teams[account_managers.index(user) % len(account_teams)]['manager_id']
        )

    print(f"\nCreated {len(account_managers_create)} Account Manager users and assigned to Account teams.")
    for team in account_teams:
        team_users = department_handler.get_users_in_team(team['team_id'])
        print(f"\nTeam {team['team_name']} ({team['team_number']}) Members:")
        for u in team_users:
            print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    print("\n" + "=" * 60)
    
    # Create Consultant Team under Consultancy Team
    consultant_team = department_handler.create_team_under_team(
        team_id=teams[1]['team_id'],
        team_name="Consultant Team",
        manager_id=directors[1].user_id
    )
    print(f"\nCreated consultant team under Consultancy Department: \n{consultant_team['team_id']}: {consultant_team['team_name']}, Manager: {user_handler.get_user(consultant_team['manager_id']).name}, Team Number: {consultant_team['team_number']}")

    # Create Consultants under Consultant Team
    consultants_create = [
        {"name": "Celine Ng", "email": "celine.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Daniel Tan", "email": "daniel.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Fiona Lim", "email": "fiona.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "George Lee", "email": "george.lee@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Hannah Wong", "email": "hannah.wong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Irfan Malik", "email": "irfan.malik@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Janice Tan", "email": "janice.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Karthik Pillai", "email": "karthik.pillai@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Liyana Osman", "email": "liyana.osman@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Marcus Tan", "email": "marcus.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Nadia Binte Hassan", "email": "nadia.hassan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Neha Raj", "email": "neha.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Patrick Ong", "email": "patrick.ong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Pravin Nair", "email": "pravin.nair@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rachel Teo", "email": "rachel.teo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rafiq Abdullah", "email": "rafiq.abdullah@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Ramesh Subramaniam", "email": "ramesh.subramaniam@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rebecca Tan", "email": "rebecca.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rosalind Goh", "email": "rosalind.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Siti Mariam", "email": "siti.mariam@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Suresh Kumar", "email": "suresh.kumar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Tan Wei Ling", "email": "tan.weiling@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Thiru Rajan", "email": "thiru.rajan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Uma Devi", "email": "uma.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Vanessa Koh", "email": "vanessa.koh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Vijay Menon", "email": "vijay.menon@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Wong Jia Hui", "email": "wong.jiahui@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Yasmin Salleh", "email": "yasmin.salleh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Zachary Lim", "email": "zachary.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Zulkifli Hassan", "email": "zulkifli.hassan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
    ]

    consultants = []
    for user_data in consultants_create:
        user = user_handler.create_user(**user_data)
        consultants.append(user)
        department_handler.assign_user_to_team(
            team_id=consultant_team['team_id'],
            user_id=user.user_id,
            manager_id=consultant_team['manager_id']
        )
    
    print(f"\nCreated {len(consultants_create)} consultant users and assigned to Consultant Team.")
    team_users = department_handler.get_users_in_team(consultant_team['team_id'])
    print(f"\nTeam {consultant_team['team_name']} ({consultant_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    
    print("\n" + "=" * 60)

   # Create Developers team and Support team under System Solutioning Team
    developers_team = department_handler.create_team_under_team(
        team_id=teams[2]['team_id'],
        team_name="Developers Team",
        manager_id=directors[2].user_id
    )
    support_team = department_handler.create_team_under_team(
        team_id=teams[2]['team_id'],
        team_name="Support Team",
        manager_id=directors[2].user_id
    )
    print(f"\nCreated Developers team under System Solutioning Department: \n{developers_team['team_id']}: {developers_team['team_name']}, Manager: {user_handler.get_user(developers_team['manager_id']).name}, Team Number: {developers_team['team_number']}")
    print(f"\nCreated Support team under System Solutioning Department: \n{support_team['team_id']}: {support_team['team_name']}, Manager: {user_handler.get_user(support_team['manager_id']).name}, Team Number: {support_team['team_number']}")

    # Create Developers team users
    developers_create = [
        {"name": "Adeline Lim", "email": "adeline.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Ahmad Faisal", "email": "ahmad.faisal@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Alicia Goh", "email": "alicia.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aminah Binte Zainal", "email": "aminah.zainal@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Andrew Koh", "email": "andrew.koh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Anjali Devi", "email": "anjali.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Arif Abdullah", "email": "arif.abdullah@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Audrey Ng", "email": "audrey.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Benjamin Toh", "email": "benjamin.toh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Bryan Lee", "email": "bryan.lee@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Cheryl Tan", "email": "cheryl.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Chong Wei", "email": "chong.wei@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Daniel Ong", "email": "daniel.ong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Deepa Menon", "email": "deepa.menon@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Diana Chua", "email": "diana.chua@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Edward Lim", "email": "edward.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elaine Koh", "email": "elaine.koh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Farid Jamal", "email": "farid.jamal@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Fatimah Noor", "email": "fatimah.noor@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Gavin Teo", "email": "gavin.teo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Gurinder Singh", "email": "gurinder.singh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Hazirah Binte Ali", "email": "hazirah.ali@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Ishwar Raj", "email": "ishwar.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jacky Tan", "email": "jacky.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jasmine Lee", "email": "jasmine.lee@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jeffrey Chua", "email": "jeffrey.chua@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Josephine Ng", "email": "josephine.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Khalid Rahim", "email": "khalid.rahim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Kumar Suresh", "email": "kumar.suresh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Lydia Ho", "email": "lydia.ho@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mani Raj", "email": "mani.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mary Lim", "email": "mary.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Meera Devi", "email": "meera.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mohamed Zain", "email": "mohamed.zain@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Natalie Chan", "email": "natalie.chan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nicholas Wong", "email": "nicholas.wong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nora Binte Ahmad", "email": "nora.ahmad@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Patrick Goh", "email": "patrick.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Pravin Raj", "email": "pravin.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rahman Bakar", "email": "rahman.bakar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rani Devi", "email": "rani.devi@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Renee Tay", "email": "renee.tay@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Samuel Tan", "email": "samuel.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Sharifah Noor", "email": "sharifah.noor@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Stephanie Chia", "email": "stephanie.chia@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Syafiq Hasan", "email": "syafiq.hasan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Thomas Yeo", "email": "thomas.yeo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Vikram Pillai", "email": "vikram.pillai@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Zainab Rahman", "email": "zainab.rahman@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Zoe Lim", "email": "zoe.lim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
    ]
    developers = []
    for user_data in developers_create:
        user = user_handler.create_user(**user_data)
        developers.append(user)
        department_handler.assign_user_to_team(
            team_id=developers_team['team_id'],
            user_id=user.user_id,
            manager_id=developers_team['manager_id']
        )
    
    # Create Support team users
    support_users_create = [
        {"name": "Aaron Sim", "email": "aaron.sim@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Adib Roslan", "email": "adib.roslan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aishah Rahmat", "email": "aishah.rahmat@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Alan Quek", "email": "alan.quek@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Amanda Toh", "email": "amanda.toh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aruna Pillai", "email": "aruna.pillai@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Bala Nair", "email": "bala.nair@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Beatrice Loo", "email": "beatrice.loo@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Cecilia Ong", "email": "cecilia.ong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Chandran Menon", "email": "chandran.menon@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Clara Low", "email": "clara.low@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Darren Goh", "email": "darren.goh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Devan Raj", "email": "devan.raj@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elaine Wong", "email": "elaine.wong@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elliot Tan", "email": "elliot.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Farhana Binte Omar", "email": "farhana.omar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Florence Koh", "email": "florence.koh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Goh Wei Lun", "email": "goh.weilun@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Harini Krishnan", "email": "harini.krishnan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Hazim Bin Salleh", "email": "hazim.salleh@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Isabella Ng", "email": "isabella.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jacob Lee", "email": "jacob.lee@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jaya Narayan", "email": "jaya.narayan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Joanne Tay", "email": "joanne.tay@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Karim Bin Yusuf", "email": "karim.yusuf@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Kelvin Ng", "email": "kelvin.ng@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Melissa Tan", "email": "melissa.tan@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nadiah Ali", "email": "nadiah.ali@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rajiv Pillai", "email": "rajiv.pillai@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Vanitha Kumar", "email": "vanitha.kumar@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
    ]
    support_users = []
    for user_data in support_users_create:
        user = user_handler.create_user(**user_data)
        support_users.append(user)
        department_handler.assign_user_to_team(
            team_id=support_team['team_id'],
            user_id=user.user_id,
            manager_id=support_team['manager_id']
        )

    
    print(f"\nCreated {len(developers_create)} developer users and assigned to Developers Team.")
    team_users = department_handler.get_users_in_team(developers_team['team_id'])
    print(f"\nTeam {developers_team['team_name']} ({developers_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    print(f"\nCreated {len(support_users_create)} support users and assigned to Support Team.")
    team_users = department_handler.get_users_in_team(support_team['team_id'])
    print(f"\nTeam {support_team['team_name']} ({support_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")

    print("\n" + "=" * 60)

    # Create Senior Engineer team under Engineering Operation Team
    senior_engineer_team = department_handler.create_team_under_team(
        team_id=teams[3]['team_id'],
        team_name="Senior Engineer",
        manager_id=directors[3].user_id
    )

    # Create Junior Engineer team under Engineering Operation Team
    junior_engineer_team = department_handler.create_team_under_team(
        team_id=teams[3]['team_id'],
        team_name="Junior Engineer",
        manager_id=directors[3].user_id
    )

    # Create Call Centre team under Engineering Operation Team
    call_centre_team = department_handler.create_team_under_team(
        team_id=teams[3]['team_id'],
        team_name="Call Centre",
        manager_id=directors[3].user_id
    )

    # Create Operation Planning team under Engineering Operation Team
    operation_planning_team = department_handler.create_team_under_team(
        team_id=teams[3]['team_id'],
        team_name="Operation Planning",
        manager_id=directors[3].user_id
    )

    print(f"\nCreated Senior Engineer team under Engineering Operation Department: \n{senior_engineer_team['team_id']}: {senior_engineer_team['team_name']}, Manager: {user_handler.get_user(senior_engineer_team['manager_id']).name}, Team Number: {senior_engineer_team['team_number']}")
    print(f"\nCreated Junior Engineer team under Engineering Operation Department: \n{junior_engineer_team['team_id']}: {junior_engineer_team['team_name']}, Manager: {user_handler.get_user(junior_engineer_team['manager_id']).name}, Team Number: {junior_engineer_team['team_number']}")
    print(f"\nCreated Call Centre team under Engineering Operation Department: \n{call_centre_team['team_id']}: {call_centre_team['team_name']}, Manager: {user_handler.get_user(call_centre_team['manager_id']).name}, Team Number: {call_centre_team['team_number']}")
    print(f"\nCreated Operation Planning team under Engineering Operation Department: \n{operation_planning_team['team_id']}: {operation_planning_team['team_name']}, Manager: {user_handler.get_user(operation_planning_team['manager_id']).name}, Team Number: {operation_planning_team['team_number']}")

    # Create Senior Engineers under Senior Engineer team
    senior_engineers_create = [
        {"name": "Aaron Lim", "email": "aaron.lim.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Afiq Rahman", "email": "afiq.rahman.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alvin Tan", "email": "alvin.tan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amira Binte Osman", "email": "amira.osman.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anand Raj", "email": "anand.raj.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Andrea Chua", "email": "andrea.chua.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Azim Bin Hassan", "email": "azim.hassan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bala Nair", "email": "bala.nair.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Benjamin Goh", "email": "benjamin.goh.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Brenda Tan", "email": "brenda.tan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Calvin Lim", "email": "calvin.lim.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheryl Koh", "email": "cheryl.koh.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Lee", "email": "daniel.lee.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepak Menon", "email": "deepak.menon.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Diana Wong", "email": "diana.wong.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eddy Ng", "email": "eddy.ng.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Goh", "email": "elaine.goh.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Farah Noor", "email": "farah.noor.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Faizal Ahmad", "email": "faizal.ahmad.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Tan", "email": "grace.tan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hafiz Rahman", "email": "hafiz.rahman.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Harini Devi", "email": "harini.devi.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Imran Bin Said", "email": "imran.said.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Isaac Low", "email": "isaac.low.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Janet Ng", "email": "janet.ng.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jasvinder Kaur", "email": "jasvinder.kaur.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jia Hao", "email": "jia.hao.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kavita Raj", "email": "kavita.raj.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Khairul Bin Yusof", "email": "khairul.yusof.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lydia Choo", "email": "lydia.choo.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']}
    ]
    senior_engineers = []
    for user_data in senior_engineers_create:
        user = user_handler.create_user(**user_data)
        senior_engineers.append(user)
        department_handler.assign_user_to_team(
            team_id=senior_engineer_team['team_id'],
            user_id=user.user_id,
            manager_id=senior_engineer_team['manager_id']
        )
    
    # Create Junior Engineers under Junior Engineer team
    junior_engineers_create = [
        {"name": "Adam Toh", "email": "adam.toh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Adib Rahman", "email": "adib.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alison Koh", "email": "alison.koh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aman Kumar", "email": "aman.kumar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amanda Lee", "email": "amanda.lee.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amira Noor", "email": "amira.noor.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amy Chan", "email": "amy.chan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Andre Goh", "email": "andre.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anita Devi", "email": "anita.devi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anson Chia", "email": "anson.chia.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aqilah Binte Zainal", "email": "aqilah.zainal.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Arjun Menon", "email": "arjun.menon.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ashraf Ali", "email": "ashraf.ali.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Audrey Ng", "email": "audrey.ng.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Azim Abdullah", "email": "azim.abdullah.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheng Hui", "email": "cheng.hui.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chong Li", "email": "chong.li.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clara Ong", "email": "clara.ong.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Goh", "email": "daniel.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepa Kumar", "email": "deepa.kumar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Devika Rani", "email": "devika.rani.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Dzul Rahman", "email": "dzul.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Lim", "email": "elaine.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eleanor Ng", "email": "eleanor.ng.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elina Tan", "email": "elina.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elvin Chia", "email": "elvin.chia.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Emilia Koh", "email": "emilia.koh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Francis Tay", "email": "francis.tay.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ganesh Kumar", "email": "ganesh.kumar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Gavin Ho", "email": "gavin.ho.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Geetha Devi", "email": "geetha.devi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Yeo", "email": "grace.yeo.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Haikal Osman", "email": "haikal.osman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Halimah Rahman", "email": "halimah.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Harish Nair", "email": "harish.nair.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hui Min Lim", "email": "hui.min.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ibrahim Malik", "email": "ibrahim.malik.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Indra Raj", "email": "indra.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Irene Goh", "email": "irene.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Isaac Tan", "email": "isaac.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ivan Lee", "email": "ivan.lee.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jasmine Lau", "email": "jasmine.lau.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jayden Chua", "email": "jayden.chua.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jeremy Tan", "email": "jeremy.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Joanne Chee", "email": "joanne.chee.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "John Paul", "email": "john.paul.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kamal Subramaniam", "email": "kamal.subramaniam.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Karen Lim", "email": "karen.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kavita Raj", "email": "kavita.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kelvin Tan", "email": "kelvin.tan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kenneth Ng", "email": "kenneth.ng.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kevin Goh", "email": "kevin.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Khalid Bin Ahmad", "email": "khalid.ahmad.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kimberly Lee", "email": "kimberly.lee.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kiran Raj", "email": "kiran.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Krishnan Nair", "email": "krishnan.nair.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Laila Hussain", "email": "laila.hussain.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lakshmi Devi", "email": "lakshmi.devi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lawrence Chia", "email": "lawrence.chia.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lee Jia Min", "email": "lee.jiamin.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Leong Wei Jie", "email": "leong.weijie.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Li Fang", "email": "li.fang.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lina Tan", "email": "lina.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lisa Koh", "email": "lisa.koh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Logan Raj", "email": "logan.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Louis Ong", "email": "louis.ong.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mabel Yeo", "email": "mabel.yeo.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mahesh Pillai", "email": "mahesh.pillai.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Malathi Raj", "email": "malathi.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mani Kannan", "email": "mani.kannan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Marcus Tan", "email": "marcus.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Maria Abdullah", "email": "maria.abdullah.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Matthew Toh", "email": "matthew.toh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Melissa Chan", "email": "melissa.chan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Michael Lim", "email": "michael.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mohamed Ismail", "email": "mohamed.ismail.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Muhammad Faisal", "email": "muhammad.faisal.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Muhammad Hafiz", "email": "muhammad.hafiz.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Munirah Binte Ahmad", "email": "munirah.ahmad.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nadia Lim", "email": "nadia.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nandini Raj", "email": "nandini.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Natalie Koh", "email": "natalie.koh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nathan Chia", "email": "nathan.chia.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Naveen Kumar", "email": "naveen.kumar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Neha Menon", "email": "neha.menon.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nicole Tan", "email": "nicole.tan.1@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nora Rahman", "email": "nora.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nur Aisyah", "email": "nur.aisyah.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nurul Huda", "email": "nurul.huda.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ong Jia Hao", "email": "ong.jiahao.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pavitra Devi", "email": "pavitra.devi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Peter Low", "email": "peter.low.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Prakash Nair", "email": "prakash.nair.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Priya Raj", "email": "priya.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Qamar Iskandar", "email": "qamar.iskandar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Queenie Tan", "email": "queenie.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rachel Goh", "email": "rachel.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rafiq Bin Ali", "email": "rafiq.ali.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rajesh Pillai", "email": "rajesh.pillai.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rani Kumari", "email": "rani.kumari.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Raymond Tan", "email": "raymond.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rebecca Lim", "email": "rebecca.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ridwan Ahmad", "email": "ridwan.ahmad.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rosnah Binte Omar", "email": "rosnah.omar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ruben Singh", "email": "ruben.singh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ryan Chua", "email": "ryan.chua.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sabrina Tan", "email": "sabrina.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Saidah Binte Rahman", "email": "saidah.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Samuel Lee", "email": "samuel.lee.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sangeetha Devi", "email": "sangeetha.devi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sarah Ong", "email": "sarah.ong.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sean Lim", "email": "sean.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Selina Ng", "email": "selina.ng.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shafiq Bin Hassan", "email": "shafiq.hassan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shalini Raj", "email": "shalini.raj.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sharifah Noor", "email": "sharifah.noor.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shi Hui Goh", "email": "shi.hui.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Simran Kaur", "email": "simran.kaur.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Siti Aisyah", "email": "siti.aisyah.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Soh Wei Ming", "email": "soh.weiming.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sonia Tan", "email": "sonia.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Suresh Menon", "email": "suresh.menon.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sylvia Lau", "email": "sylvia.lau.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tan Jia Yi", "email": "tan.jiayi.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tan Wei Ling", "email": "tan.weiling.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Taufiq Rahman", "email": "taufiq.rahman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Terence Chia", "email": "terence.chia.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thiru Rajan", "email": "thiru.rajan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tiffany Wong", "email": "tiffany.wong.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ting Wei", "email": "ting.wei.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Umar Hakim", "email": "umar.hakim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vani Krishnan", "email": "vani.krishnan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Varun Menon", "email": "varun.menon.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vivian Chan", "email": "vivian.chan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wei Jie Tan", "email": "wei.jie.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wendy Lim", "email": "wendy.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "William Goh", "email": "william.goh.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wong Zi Hao", "email": "wong.zihao.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Xinyi Lau", "email": "xinyi.lau.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yasmin Binte Omar", "email": "yasmin.omar.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yeo Jun Wei", "email": "yeo.junwei.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yogesh Nair", "email": "yogesh.nair.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yong Jie Lim", "email": "yongjie.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yusof Bin Abdullah", "email": "yusof.abdullah.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zachary Tan", "email": "zachary.tan.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zahid Bin Osman", "email": "zahid.osman.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zara Lim", "email": "zara.lim.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zhang Mei", "email": "zhang.mei.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zhen Hui", "email": "zhen.hui.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zubaidah Binte Ali", "email": "zubaidah.ali.2@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
    ]
    junior_engineers = []
    for user_data in junior_engineers_create:
        user = user_handler.create_user(**user_data)
        junior_engineers.append(user)
        department_handler.assign_user_to_team(
            team_id=junior_engineer_team['team_id'],
            user_id=user.user_id,
            manager_id=junior_engineer_team['manager_id']
        )

    # Create Call Centre members under Call Centre team
    call_centre_create = [
        {"name": "Adeline Goh", "email": "adeline.goh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Adib Bin Hassan", "email": "adib.hassan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aditya Kumar", "email": "aditya.kumar.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Adrian Lim", "email": "adrian.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Afiqah Noor", "email": "afiqah.noor.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aileen Ng", "email": "aileen.ng.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ajay Nair", "email": "ajay.nair.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alfred Tan", "email": "alfred.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aliyah Binte Rahman", "email": "aliyah.rahman.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amanda Koh", "email": "amanda.koh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amirah Abdullah", "email": "amirah.abdullah.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amrit Kaur", "email": "amrit.kaur.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Andrea Lee", "email": "andrea.lee.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Angela Yeo", "email": "angela.yeo.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anil Raj", "email": "anil.raj.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anisa Binte Omar", "email": "anisa.omar.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anita Devi", "email": "anita.devi.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Annabelle Tan", "email": "annabelle.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Arjun Menon", "email": "arjun.menon.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ashraf Malik", "email": "ashraf.malik.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ava Lim", "email": "ava.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ayesha Binte Ali", "email": "ayesha.ali.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Azlan Rahim", "email": "azlan.rahim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bala Krishnan", "email": "bala.krishnan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Benjamin Wong", "email": "benjamin.wong.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bernard Tan", "email": "bernard.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bryan Chua", "email": "bryan.chua.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Carmen Ong", "email": "carmen.ong.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cassandra Lim", "email": "cassandra.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Catherine Lee", "email": "catherine.lee.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chandra Raj", "email": "chandra.raj.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Charles Lim", "email": "charles.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheng Wei", "email": "cheng.wei.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheryl Tan", "email": "cheryl.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Christina Goh", "email": "christina.goh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clarence Lee", "email": "clarence.lee.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clara Chia", "email": "clara.chia.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Goh", "email": "daniel.goh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daphne Lim", "email": "daphne.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Darren Ng", "email": "darren.ng.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Debbie Yeo", "email": "debbie.yeo.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepa Raj", "email": "deepa.raj.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Diana Lim", "email": "diana.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Dominic Koh", "email": "dominic.koh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Durga Devi", "email": "durga.devi.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eddy Wong", "email": "eddy.wong.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Yeo", "email": "elaine.yeo.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eldwin Tan", "email": "eldwin.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eleanor Chua", "email": "eleanor.chua.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elizabeth Ng", "email": "elizabeth.ng.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elvin Koh", "email": "elvin.koh.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Emily Tan", "email": "emily.tan.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Emma Lee", "email": "emma.lee.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eunice Lim", "email": "eunice.lim.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Evelyn Lau", "email": "evelyn.lau.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Farhan Bin Osman", "email": "farhan.osman.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Fatimah Noor", "email": "fatimah.noor.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Fazli Rahman", "email": "fazli.rahman.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Felix Ong", "email": "felix.ong.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Fiona Tay", "email": "fiona.tay.4@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
    ]
    call_centre_members = []
    for user_data in call_centre_create:
        user = user_handler.create_user(**user_data)
        call_centre_members.append(user)
        department_handler.assign_user_to_team(
            team_id=call_centre_team['team_id'],
            user_id=user.user_id,
            manager_id=call_centre_team['manager_id']
        )
    
    # Create Operation Planning members under Operation Planning Team
    operation_planning_create = [
        {"name": "Aaron Tan", "email": "aaron.tan.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Abdul Rahman", "email": "abdul.rahman.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aileen Low", "email": "aileen.low.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aisha Binte Salleh", "email": "aisha.salleh.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alan Chia", "email": "alan.chia.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amarjit Singh", "email": "amarjit.singh.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amy Koh", "email": "amy.koh.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anita Lim", "email": "anita.lim.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Arjun Nair", "email": "arjun.nair.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aziz Bin Osman", "email": "aziz.osman.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Beatrice Ng", "email": "beatrice.ng.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bryan Lim", "email": "bryan.lim.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cassandra Tan", "email": "cassandra.tan.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Celine Phua", "email": "celine.phua.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Charlene Goh", "email": "charlene.goh.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chen Wei", "email": "chen.wei.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clara Yeo", "email": "clara.yeo.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Toh", "email": "daniel.toh.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepa Rani", "email": "deepa.rani.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Dinesh Kumar", "email": "dinesh.kumar.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eddy Tan", "email": "eddy.tan.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Wong", "email": "elaine.wong.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Farhan Iskandar", "email": "farhan.iskandar.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Fiona Teo", "email": "fiona.teo.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Gavin Ong", "email": "gavin.ong.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Geetha Krishnan", "email": "geetha.krishnan.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Lee", "email": "grace.lee.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hakim Ali", "email": "hakim.ali.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hannah Chee", "email": "hannah.chee.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Irfan Bin Rahim", "email": "irfan.rahim.3@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
    ]
    operation_planning_members = []
    for user_data in operation_planning_create:
        user = user_handler.create_user(**user_data)
        operation_planning_members.append(user)
        department_handler.assign_user_to_team(
            team_id=operation_planning_team['team_id'],
            user_id=user.user_id,
            manager_id=operation_planning_team['manager_id']
        )
    
    print(f"\nCreated {len(senior_engineers)} senior engineers users and assigned to Senior Engineer Team.")
    team_users = department_handler.get_users_in_team(senior_engineer_team['team_id'])
    print(f"\nTeam {senior_engineer_team['team_name']} ({senior_engineer_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")

    print(f"\nCreated {len(junior_engineers)} junior engineer users and assigned to Junior Engineer Team.")
    team_users = department_handler.get_users_in_team(junior_engineer_team['team_id'])
    print(f"\nTeam {junior_engineer_team['team_name']} ({junior_engineer_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")

    print(f"\nCreated {len(call_centre_members)} call centre users and assigned to Call Centre Team.")
    team_users = department_handler.get_users_in_team(call_centre_team['team_id'])
    print(f"\nTeam {call_centre_team['team_name']} ({call_centre_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")

    print(f"\nCreated {len(operation_planning_members)} operation planning users and assigned to Operation Planning Team.")
    team_users = department_handler.get_users_in_team(operation_planning_team['team_id'])
    print(f"\nTeam {operation_planning_team['team_name']} ({operation_planning_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")


    print("\n" + "=" * 60)


    # Create HR team, L&D team, and Admin team under HR and Admin team
    hr_team = department_handler.create_team_under_team(
        team_id=teams[4]['team_id'],
        team_name="HR",
        manager_id=directors[4].user_id
    )
    lnd_team = department_handler.create_team_under_team(
        team_id=teams[4]['team_id'],
        team_name="L&D",
        manager_id=directors[4].user_id
    )
    admin_team = department_handler.create_team_under_team(
        team_id=teams[4]['team_id'],
        team_name="Admin",
        manager_id=directors[4].user_id
    )

    print(f"\nCreated HR team under HR and Admin Department: \n{hr_team['team_id']}: {hr_team['team_name']}, Manager: {user_handler.get_user(hr_team['manager_id']).name}, Team Number: {hr_team['team_number']}")
    print(f"\nCreated L&D team under HR and Admin Department: \n{lnd_team['team_id']}: {lnd_team['team_name']}, Manager: {user_handler.get_user(lnd_team['manager_id']).name}, Team Number: {lnd_team['team_number']}")
    print(f"\nCreated Admin team under HR and Admin Department: \n{admin_team['team_id']}: {admin_team['team_name']}, Manager: {user_handler.get_user(admin_team['manager_id']).name}, Team Number: {admin_team['team_number']}")

    # Create HR members under HR team
    hr_create = [
        
    ]







if __name__ == "__main__":
    seed_database()