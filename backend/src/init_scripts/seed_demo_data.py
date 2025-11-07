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

    print(f"\nCreated department: \n{c_suite_dept['department_id']}: {c_suite_dept['department_name']}, Manager ID: {c_suite_dept['manager_id']}")
    print("\n" + "=" * 60)

    # Create Directors
    directors_create = [
        {"name": "Derek Tan", "email": "derek.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Ernst Sim", "email": "ernst.sim.cons@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Eric Loh", "email": "eric.loh.ssd@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Philip Lee", "email": "philip.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Sally Loh", "email": "sally.loh.hr@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "David Yap", "email": "david.yap.fin@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
        {"name": "Peter Yap", "email": "peter.yap.it@kira.ai", "password": "Password123!", "role": UserRole.DIRECTOR, "admin": True, "department_id": c_suite_dept['department_id']},
    ]

    directors = []
    for director_data in directors_create:
        director = user_handler.create_user(**director_data)
        directors.append(director)
    
    print(f"\nCreated {len(directors)} director users.")
    for director in directors:
        print(f"{director.user_id}: {director.name}, {director.email}, {department_handler.view_department_by_id(director.department_id)['department_name']}")
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

    # Create Sales Manager Team under Sales Department
    sales_team = department_handler.create_team_under_department(department_id=departments[0]['department_id'], team_name="Sales Manager", manager_id=directors[0].user_id)

    # Sales Team Managers
    sales_users_create = [
        {"name": "Alice Tan", "email": "alice.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Bob Lim", "email": "bob.lim.sales@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Charlie Lee", "email": "charlie.lee.sales@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Diana Ong", "email": "diana.ong.sales@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Devi Vishwakumar", "email": "devi.vishwakumar.sales@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[0]['department_id']},
    ]
    sales_managers = []
    for user_data in sales_users_create:
        user = user_handler.create_user(**user_data)
        sales_managers.append(user)
        department_handler.assign_user_to_team(team_id=sales_team['team_id'], user_id=user.user_id, manager_id=sales_team['manager_id'])

    print(f"\nCreated {len(sales_users_create)} sales team managers.")
    for user in sales_managers:
        print(f"{user.user_id}: {user.name}, {user.email}, {department_handler.view_department_by_id(user.department_id)['department_name']}, Assigned to Team: {sales_team['team_number']}, Manager: {user_handler.get_user(sales_team['manager_id']).name}")

    print("\n" + "=" * 60)

    # Create Account Teams under Sales Manager Team
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
            team_id=sales_team['team_id'],
            team_name=team_data['team_name'],
            manager_id=team_data['manager_id']
        )
        account_teams.append(team)

    print(f"\nCreated {len(account_teams)} account teams under Sales department.")
    for team in account_teams:
        print(f"{team['team_id']}: {team['team_name']}, Manager: {user_handler.get_user(team['manager_id']).name}, Team Number: {team['team_number']}")
    
    # Create Account Managers under Account Teams
    account_managers_create = [
        {"name": "Aisha Rahman", "email": "aisha.rahman.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Amarjit Singh", "email": "amarjit.singh.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Angeline Lim", "email": "angeline.lim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Arun Nair", "email": "arun.nair.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Benjamin Lee", "email": "benjamin.lee.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Bryan Ong", "email": "bryan.ong.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Cassandra Tay", "email": "cassandra.tay.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Cheryl Chan", "email": "cheryl.chan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Daniel Low", "email": "daniel.low.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Dinesh Pillai", "email": "dinesh.pillai.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Eddie Phua", "email": "eddie.phua.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Elaine Tan", "email": "elaine.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Farah Binte Ahmad", "email": "farah.ahmad.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Faizal Osman", "email": "faizal.osman.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Fiona Goh", "email": "fiona.goh.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Gurpreet Kaur", "email": "gurpreet.kaur.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Hannah Chia", "email": "hannah.chia.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Harith Iskandar", "email": "harith.iskandar.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Ian Foo", "email": "ian.foo.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Irfan Yusof", "email": "irfan.yusof.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jacqueline Lim", "email": "jacqueline.lim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "James Pang", "email": "james.pang.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Janice Ho", "email": "janice.ho.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jasdeep Singh", "email": "jasdeep.singh.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jennifer Tan", "email": "jennifer.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Jeremy Ong", "email": "jeremy.ong.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Joanne Lim", "email": "joanne.lim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Joseph Tan", "email": "joseph.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kavitha Raj", "email": "kavitha.raj.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kelvin Chong", "email": "kelvin.chong.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kenneth Chew", "email": "kenneth.chew.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kevin Ng", "email": "kevin.ng.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Khairul Anwar", "email": "khairul.anwar.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kimberly Teo", "email": "kimberly.teo.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Kiran Subramaniam", "email": "kiran.subramaniam.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Lakshmi Devi", "email": "lakshmi.devi.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Lawrence Tan", "email": "lawrence.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Liyana Binte Noor", "email": "liyana.noor.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Maria Abdullah", "email": "maria.abdullah.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Mei Ling Tan", "email": "meiling.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Muthu Krishnan", "email": "muthu.krishnan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nadia Salleh", "email": "nadia.salleh.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nirmala Devi", "email": "nirmala.devi.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Nurul Iman", "email": "nurul.iman.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Patrick Lim", "email": "patrick.lim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Pritam Kaur", "email": "pritam.kaur.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Rajesh Menon", "email": "rajesh.menon.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Ramesh Nair", "email": "ramesh.nair.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Roslan Bakar", "email": "roslan.bakar.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Siti Nurhaliza", "email": "siti.nurhaliza.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Stephanie Wong", "email": "stephanie.wong.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Suria Binte Ahmad", "email": "suria.ahmad.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Tan Wei Jie", "email": "tan.weijie.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Thomas Cheong", "email": "thomas.cheong.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Umar Hakim", "email": "umar.hakim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Vanessa Tan", "email": "vanessa.tan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Wei Ming Goh", "email": "weiming.goh.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Yasmin Ali", "email": "yasmin.ali.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Zulfiqar Hassan", "email": "zulfiqar.hassan.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']},
        {"name": "Zuraidah Binte Rahim", "email": "zuraidah.rahim.sales@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[0]['department_id']}
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
    
    # Create Consultant Team under Consultancy Department
    consultant_team = department_handler.create_team_under_department(
        department_id=departments[1]['department_id'],
        team_name="Consultant",
        manager_id=directors[1].user_id
    )
    print(f"\nCreated consultant team under Consultancy Department: \n{consultant_team['team_id']}: {consultant_team['team_name']}, Manager: {user_handler.get_user(consultant_team['manager_id']).name}, Team Number: {consultant_team['team_number']}")

    # Create Consultants under Consultant Team
    consultants_create = [
        {"name": "Celine Ng", "email": "celine.ng.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Daniel Tan", "email": "daniel.tan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Fiona Lim", "email": "fiona.lim.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "George Lee", "email": "george.lee.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Hannah Wong", "email": "hannah.wong.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Irfan Malik", "email": "irfan.malik.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Janice Tan", "email": "janice.tan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Karthik Pillai", "email": "karthik.pillai.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Liyana Osman", "email": "liyana.osman.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Marcus Tan", "email": "marcus.tan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Nadia Binte Hassan", "email": "nadia.hassan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Neha Raj", "email": "neha.raj.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Patrick Ong", "email": "patrick.ong.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Pravin Nair", "email": "pravin.nair.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rachel Teo", "email": "rachel.teo.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rafiq Abdullah", "email": "rafiq.abdullah.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Ramesh Subramaniam", "email": "ramesh.subramaniam.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rebecca Tan", "email": "rebecca.tan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Rosalind Goh", "email": "rosalind.goh.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Siti Mariam", "email": "siti.mariam.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Suresh Kumar", "email": "suresh.kumar.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Tan Wei Ling", "email": "tan.weiling.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Thiru Rajan", "email": "thiru.rajan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Uma Devi", "email": "uma.devi.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Vanessa Koh", "email": "vanessa.koh.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Vijay Menon", "email": "vijay.menon.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Wong Jia Hui", "email": "wong.jiahui.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Yasmin Salleh", "email": "yasmin.salleh.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Zachary Lim", "email": "zachary.lim.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
        {"name": "Zulkifli Hassan", "email": "zulkifli.hassan.cons@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[1]['department_id']},
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

   # Create Developers team and Support team under System Solutioning Department
    developers_team = department_handler.create_team_under_department(
        department_id=departments[2]['department_id'],
        team_name="Developers",
        manager_id=directors[2].user_id
    )
    support_team = department_handler.create_team_under_department(
        department_id=departments[2]['department_id'],
        team_name="Support Team",
        manager_id=directors[2].user_id
    )
    print(f"\nCreated Developers team under System Solutioning Department: \n{developers_team['team_id']}: {developers_team['team_name']}, Manager: {user_handler.get_user(developers_team['manager_id']).name}, Team Number: {developers_team['team_number']}")
    print(f"\nCreated Support team under System Solutioning Department: \n{support_team['team_id']}: {support_team['team_name']}, Manager: {user_handler.get_user(support_team['manager_id']).name}, Team Number: {support_team['team_number']}")

    # Create Developers team users
    developers_create = [
        {"name": "Adeline Lim", "email": "adeline.lim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Ahmad Faisal", "email": "ahmad.faisal.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Alicia Goh", "email": "alicia.goh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aminah Binte Zainal", "email": "aminah.zainal.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Andrew Koh", "email": "andrew.koh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Anjali Devi", "email": "anjali.devi.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Arif Abdullah", "email": "arif.abdullah.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Audrey Ng", "email": "audrey.ng.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Benjamin Toh", "email": "benjamin.toh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Bryan Lee", "email": "bryan.lee.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Cheryl Tan", "email": "cheryl.tan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Chong Wei", "email": "chong.wei.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Daniel Ong", "email": "daniel.ong.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Deepa Menon", "email": "deepa.menon.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Diana Chua", "email": "diana.chua.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Edward Lim", "email": "edward.lim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elaine Koh", "email": "elaine.koh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Farid Jamal", "email": "farid.jamal.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Fatimah Noor", "email": "fatimah.noor.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Gavin Teo", "email": "gavin.teo.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Gurinder Singh", "email": "gurinder.singh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Hazirah Binte Ali", "email": "hazirah.ali.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Ishwar Raj", "email": "ishwar.raj.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jacky Tan", "email": "jacky.tan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jasmine Lee", "email": "jasmine.lee.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jeffrey Chua", "email": "jeffrey.chua.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Josephine Ng", "email": "josephine.ng.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Khalid Rahim", "email": "khalid.rahim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Kumar Suresh", "email": "kumar.suresh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Lydia Ho", "email": "lydia.ho.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mani Raj", "email": "mani.raj.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mary Lim", "email": "mary.lim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Meera Devi", "email": "meera.devi.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Mohamed Zain", "email": "mohamed.zain.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Natalie Chan", "email": "natalie.chan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nicholas Wong", "email": "nicholas.wong.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nora Binte Ahmad", "email": "nora.ahmad.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Patrick Goh", "email": "patrick.goh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Pravin Raj", "email": "pravin.raj.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rahman Bakar", "email": "rahman.bakar.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rani Devi", "email": "rani.devi.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Renee Tay", "email": "renee.tay.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Samuel Tan", "email": "samuel.tan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Sharifah Noor", "email": "sharifah.noor.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Stephanie Chia", "email": "stephanie.chia.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Syafiq Hasan", "email": "syafiq.hasan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Thomas Yeo", "email": "thomas.yeo.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Vikram Pillai", "email": "vikram.pillai.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Zainab Rahman", "email": "zainab.rahman.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Zoe Lim", "email": "zoe.lim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
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
        {"name": "Aaron Sim", "email": "aaron.sim.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Adib Roslan", "email": "adib.roslan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aishah Rahmat", "email": "aishah.rahmat.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Alan Quek", "email": "alan.quek.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Amanda Toh", "email": "amanda.toh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Aruna Pillai", "email": "aruna.pillai.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Bala Nair", "email": "bala.nair.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Beatrice Loo", "email": "beatrice.loo.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Cecilia Ong", "email": "cecilia.ong.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Chandran Menon", "email": "chandran.menon.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Clara Low", "email": "clara.low.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Darren Goh", "email": "darren.goh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Devan Raj", "email": "devan.raj.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elaine Wong", "email": "elaine.wong.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Elliot Tan", "email": "elliot.tan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Farhana Binte Omar", "email": "farhana.omar.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Florence Koh", "email": "florence.koh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Goh Wei Lun", "email": "goh.weilun.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Harini Krishnan", "email": "harini.krishnan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Hazim Bin Salleh", "email": "hazim.salleh.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Isabella Ng", "email": "isabella.ng.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jacob Lee", "email": "jacob.lee.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Jaya Narayan", "email": "jaya.narayan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Joanne Tay", "email": "joanne.tay.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Karim Bin Yusuf", "email": "karim.yusuf.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Kelvin Ng", "email": "kelvin.ng.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Melissa Tan", "email": "melissa.tan.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Nadiah Ali", "email": "nadiah.ali.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Rajiv Pillai", "email": "rajiv.pillai.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
        {"name": "Vanitha Kumar", "email": "vanitha.kumar.ssd@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[2]['department_id']},
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

    # Create Senior Engineer team under Engineering Operation Department
    senior_engineer_team = department_handler.create_team_under_department(
        department_id=departments[3]['department_id'],
        team_name="Senior Engineers",
        manager_id=directors[3].user_id
    )

    # Create Junior Engineer team under Engineering Operation Department
    junior_engineer_team = department_handler.create_team_under_department(
        department_id=departments[3]['department_id'],
        team_name="Junior Engineers",
        manager_id=directors[3].user_id
    )

    # Create Call Centre team under Engineering Operation Department
    call_centre_team = department_handler.create_team_under_department(
        department_id=departments[3]['department_id'],
        team_name="Call Centre",
        manager_id=directors[3].user_id
    )

    # Create Operation Planning team under Engineering Operation Department
    operation_planning_team = department_handler.create_team_under_department(
        department_id=departments[3]['department_id'],
        team_name="Operation Planning",
        manager_id=directors[3].user_id
    )

    print(f"\nCreated Senior Engineer team under Engineering Operation Department: \n{senior_engineer_team['team_id']}: {senior_engineer_team['team_name']}, Manager: {user_handler.get_user(senior_engineer_team['manager_id']).name}, Team Number: {senior_engineer_team['team_number']}")
    print(f"\nCreated Junior Engineer team under Engineering Operation Department: \n{junior_engineer_team['team_id']}: {junior_engineer_team['team_name']}, Manager: {user_handler.get_user(junior_engineer_team['manager_id']).name}, Team Number: {junior_engineer_team['team_number']}")
    print(f"\nCreated Call Centre team under Engineering Operation Department: \n{call_centre_team['team_id']}: {call_centre_team['team_name']}, Manager: {user_handler.get_user(call_centre_team['manager_id']).name}, Team Number: {call_centre_team['team_number']}")
    print(f"\nCreated Operation Planning team under Engineering Operation Department: \n{operation_planning_team['team_id']}: {operation_planning_team['team_name']}, Manager: {user_handler.get_user(operation_planning_team['manager_id']).name}, Team Number: {operation_planning_team['team_number']}")

    # Create Senior Engineers under Senior Engineer team
    senior_engineers_create = [
        {"name": "Alvin Tan", "email": "alvin.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anand Raj", "email": "anand.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Andrea Chua", "email": "andrea.chua.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Azim Bin Hassan", "email": "azim.hassan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Benjamin Goh", "email": "benjamin.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Brenda Tan", "email": "brenda.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Calvin Lim", "email": "calvin.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheryl Koh", "email": "cheryl.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Diana Wong", "email": "diana.wong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eddy Ng", "email": "eddy.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Goh", "email": "elaine.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Farah Noor", "email": "farah.noor.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Faizal Ahmad", "email": "faizal.ahmad.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Tan", "email": "grace.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hafiz Rahman", "email": "hafiz.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Isaac Low", "email": "isaac.low.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Janet Ng", "email": "janet.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jasvinder Kaur", "email": "jasvinder.kaur.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Khairul Bin Yusof", "email": "khairul.yusof.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lydia Choo", "email": "lydia.choo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']}
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
        {"name": "Adam Toh", "email": "adam.toh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Adib Rahman", "email": "adib.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alison Koh", "email": "alison.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aman Kumar", "email": "aman.kumar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amanda Lee", "email": "amanda.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amira Noor", "email": "amira.noor.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amy Chan", "email": "amy.chan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Andre Goh", "email": "andre.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anita Devi", "email": "anita.devi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anson Chia", "email": "anson.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aqilah Binte Zainal", "email": "aqilah.zainal.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Arjun Menon", "email": "arjun.menon.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ashraf Ali", "email": "ashraf.ali.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Audrey Ng", "email": "audrey.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Azim Abdullah", "email": "azim.abdullah.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cheng Hui", "email": "cheng.hui.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chong Li", "email": "chong.li.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clara Ong", "email": "clara.ong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Goh", "email": "daniel.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepa Kumar", "email": "deepa.kumar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Devika Rani", "email": "devika.rani.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Dzul Rahman", "email": "dzul.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Lim", "email": "elaine.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eleanor Ng", "email": "eleanor.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elina Tan", "email": "elina.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elvin Chia", "email": "elvin.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Emilia Koh", "email": "emilia.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Francis Tay", "email": "francis.tay.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ganesh Kumar", "email": "ganesh.kumar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Gavin Ho", "email": "gavin.ho.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Geetha Devi", "email": "geetha.devi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Yeo", "email": "grace.yeo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Haikal Osman", "email": "haikal.osman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Halimah Rahman", "email": "halimah.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Harish Nair", "email": "harish.nair.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hui Min Lim", "email": "hui.min.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ibrahim Malik", "email": "ibrahim.malik.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Indra Raj", "email": "indra.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Irene Goh", "email": "irene.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Isaac Tan", "email": "isaac.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ivan Lee", "email": "ivan.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jasmine Lau", "email": "jasmine.lau.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jayden Chua", "email": "jayden.chua.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jeremy Tan", "email": "jeremy.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Joanne Chee", "email": "joanne.chee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "John Paul", "email": "john.paul.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kamal Subramaniam", "email": "kamal.subramaniam.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Karen Lim", "email": "karen.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kavita Raj", "email": "kavita.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kelvin Tan", "email": "kelvin.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kenneth Ng", "email": "kenneth.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kevin Goh", "email": "kevin.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Khalid Bin Ahmad", "email": "khalid.ahmad.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kimberly Lee", "email": "kimberly.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kiran Raj", "email": "kiran.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Krishnan Nair", "email": "krishnan.nair.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Laila Hussain", "email": "laila.hussain.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lakshmi Devi", "email": "lakshmi.devi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lawrence Chia", "email": "lawrence.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lee Jia Min", "email": "lee.jiamin.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Leong Wei Jie", "email": "leong.weijie.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Li Fang", "email": "li.fang.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lina Tan", "email": "lina.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lisa Koh", "email": "lisa.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Logan Raj", "email": "logan.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Louis Ong", "email": "louis.ong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mabel Yeo", "email": "mabel.yeo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mahesh Pillai", "email": "mahesh.pillai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Malathi Raj", "email": "malathi.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mani Kannan", "email": "mani.kannan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Marcus Tan", "email": "marcus.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Maria Abdullah", "email": "maria.abdullah.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Matthew Toh", "email": "matthew.toh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Melissa Chan", "email": "melissa.chan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Michael Lim", "email": "michael.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mohamed Ismail", "email": "mohamed.ismail.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Muhammad Faisal", "email": "muhammad.faisal.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Muhammad Hafiz", "email": "muhammad.hafiz.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Munirah Binte Ahmad", "email": "munirah.ahmad.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nadia Lim", "email": "nadia.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nandini Raj", "email": "nandini.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Natalie Koh", "email": "natalie.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nathan Chia", "email": "nathan.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Naveen Kumar", "email": "naveen.kumar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Neha Menon", "email": "neha.menon.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nicole Tan", "email": "nicole.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nora Rahman", "email": "nora.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nur Aisyah", "email": "nur.aisyah.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nurul Huda", "email": "nurul.huda.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ong Jia Hao", "email": "ong.jiahao.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pavitra Devi", "email": "pavitra.devi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Peter Low", "email": "peter.low.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Prakash Nair", "email": "prakash.nair.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Priya Raj", "email": "priya.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Qamar Iskandar", "email": "qamar.iskandar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Queenie Tan", "email": "queenie.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rachel Goh", "email": "rachel.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rafiq Bin Ali", "email": "rafiq.ali.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rajesh Pillai", "email": "rajesh.pillai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rani Kumari", "email": "rani.kumari.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Raymond Tan", "email": "raymond.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rebecca Lim", "email": "rebecca.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ridwan Ahmad", "email": "ridwan.ahmad.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rosnah Binte Omar", "email": "rosnah.omar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ruben Singh", "email": "ruben.singh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ryan Chua", "email": "ryan.chua.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sabrina Tan", "email": "sabrina.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Saidah Binte Rahman", "email": "saidah.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Samuel Lee", "email": "samuel.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sangeetha Devi", "email": "sangeetha.devi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sarah Ong", "email": "sarah.ong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sean Lim", "email": "sean.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Selina Ng", "email": "selina.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shafiq Bin Hassan", "email": "shafiq.hassan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shalini Raj", "email": "shalini.raj.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sharifah Noor", "email": "sharifah.noor.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Shi Hui Goh", "email": "shi.hui.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Simran Kaur", "email": "simran.kaur.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Siti Aisyah", "email": "siti.aisyah.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Soh Wei Ming", "email": "soh.weiming.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sonia Tan", "email": "sonia.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Suresh Menon", "email": "suresh.menon.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sylvia Lau", "email": "sylvia.lau.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tan Jia Yi", "email": "tan.jiayi.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tan Wei Ling", "email": "tan.weiling.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Taufiq Rahman", "email": "taufiq.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Terence Chia", "email": "terence.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thiru Rajan", "email": "thiru.rajan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tiffany Wong", "email": "tiffany.wong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ting Wei", "email": "ting.wei.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Umar Hakim", "email": "umar.hakim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vani Krishnan", "email": "vani.krishnan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Varun Menon", "email": "varun.menon.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vivian Chan", "email": "vivian.chan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wei Jie Tan", "email": "wei.jie.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wendy Lim", "email": "wendy.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "William Goh", "email": "william.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Wong Zi Hao", "email": "wong.zihao.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Xinyi Lau", "email": "xinyi.lau.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yasmin Binte Omar", "email": "yasmin.omar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yeo Jun Wei", "email": "yeo.junwei.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yogesh Nair", "email": "yogesh.nair.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yong Jie Lim", "email": "yongjie.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yusof Bin Abdullah", "email": "yusof.abdullah.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zachary Tan", "email": "zachary.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zahid Bin Osman", "email": "zahid.osman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zara Lim", "email": "zara.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zhang Mei", "email": "zhang.mei.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zhen Hui", "email": "zhen.hui.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Zubaidah Binte Ali", "email": "zubaidah.ali.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
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
        {"name": "An Nguyen", "email": "an.nguyen.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bao Tran", "email": "bao.tran.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chi Pham", "email": "chi.pham.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Duy Le", "email": "duy.le.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hang Vu", "email": "hang.vu.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hien Do", "email": "hien.do.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hoa Bui", "email": "hoa.bui.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Huong Phan", "email": "huong.phan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Khanh Nguyen", "email": "khanh.nguyen.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lan Tran", "email": "lan.tran.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Linh Vo", "email": "linh.vo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Long Pham", "email": "long.pham.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Mai Le", "email": "mai.le.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Minh Vu", "email": "minh.vu.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nam Hoang", "email": "nam.hoang.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Nga Doan", "email": "nga.doan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Ngoc Pham", "email": "ngoc.pham.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Phong Bui", "email": "phong.bui.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Quang Le", "email": "quang.le.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thanh Nguyen", "email": "thanh.nguyen.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thao Tran", "email": "thao.tran.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thi Phan", "email": "thi.phan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tien Do", "email": "tien.do.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Trang Nguyen", "email": "trang.nguyen.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tuan Anh", "email": "tuan.anh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Van Le", "email": "van.le.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vy Tran", "email": "vy.tran.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yen Bui", "email": "yen.bui.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anh Dao", "email": "anh.dao.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bao Chau", "email": "bao.chau.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chaiwat Suksan", "email": "chaiwat.suksan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daran Kittisak", "email": "daran.kittisak.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Jariya Boonmee", "email": "jariya.boonmee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kanya Rattanakorn", "email": "kanya.rattanakorn.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Kittipong Sornchai", "email": "kittipong.sornchai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Lalita Sukanya", "email": "lalita.sukanya.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Manop Theerasak", "email": "manop.theerasak.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Meena Saowalak", "email": "meena.saowalak.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Niran Boonchai", "email": "niran.boonchai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Noi Chatchai", "email": "noi.chatchai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Oranuch Kittiya", "email": "oranuch.kittiya.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pailin Anong", "email": "pailin.anong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Panya Boonsri", "email": "panya.boonsri.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Parinya Suriya", "email": "parinya.suriya.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pat Boonrak", "email": "pat.boonrak.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Phawit Thongchai", "email": "phawit.thongchai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pimdao Wichuda", "email": "pimdao.wichuda.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Pornchai Niran", "email": "pornchai.niran.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rachanee Tida", "email": "rachanee.tida.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Rattanakorn Suriya", "email": "rattanakorn.suriya.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Sanan Boonmee", "email": "sanan.boonmee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Siriporn Duangjai", "email": "siriporn.duangjai.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Somchai Prasert", "email": "somchai.prasert.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Suda Anan", "email": "suda.anan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Supaporn Nattapong", "email": "supaporn.nattapong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Tanin Preecha", "email": "tanin.preecha.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Thitima Kanya", "email": "thitima.kanya.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Vichai Rung", "email": "vichai.rung.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Warin Chanan", "email": "warin.chanan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yada Pranee", "email": "yada.pranee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Yotin Sombat", "email": "yotin.sombat.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
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
        {"name": "Aaron Tan", "email": "aaron.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Abdul Rahman", "email": "abdul.rahman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aileen Low", "email": "aileen.low.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aisha Binte Salleh", "email": "aisha.salleh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Alan Chia", "email": "alan.chia.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amarjit Singh", "email": "amarjit.singh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Amy Koh", "email": "amy.koh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Anita Lim", "email": "anita.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Arjun Nair", "email": "arjun.nair.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Aziz Bin Osman", "email": "aziz.osman.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Beatrice Ng", "email": "beatrice.ng.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Bryan Lim", "email": "bryan.lim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Cassandra Tan", "email": "cassandra.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Celine Phua", "email": "celine.phua.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Charlene Goh", "email": "charlene.goh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Chen Wei", "email": "chen.wei.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Clara Yeo", "email": "clara.yeo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Daniel Toh", "email": "daniel.toh.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Deepa Rani", "email": "deepa.rani.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Dinesh Kumar", "email": "dinesh.kumar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Eddy Tan", "email": "eddy.tan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Elaine Wong", "email": "elaine.wong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Farhan Iskandar", "email": "farhan.iskandar.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Fiona Teo", "email": "fiona.teo.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Gavin Ong", "email": "gavin.ong.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Geetha Krishnan", "email": "geetha.krishnan.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Grace Lee", "email": "grace.lee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hakim Ali", "email": "hakim.ali.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Hannah Chee", "email": "hannah.chee.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
        {"name": "Irfan Bin Rahim", "email": "irfan.rahim.eod@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[3]['department_id']},
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


    # Create HR team, L&D team, and Admin team under HR and Admin Department
    hr_team = department_handler.create_team_under_department(
        department_id=departments[4]['department_id'],
        team_name="HR",
        manager_id=directors[4].user_id
    )
    lnd_team = department_handler.create_team_under_department(
        department_id=departments[4]['department_id'],
        team_name="L&D",
        manager_id=directors[4].user_id
    )
    admin_team = department_handler.create_team_under_department(
        department_id=departments[4]['department_id'],
        team_name="Admin",
        manager_id=directors[4].user_id
    )

    print(f"\nCreated HR team under HR and Admin Department: \n{hr_team['team_id']}: {hr_team['team_name']}, Manager: {user_handler.get_user(hr_team['manager_id']).name}, Team Number: {hr_team['team_number']}")
    print(f"\nCreated L&D team under HR and Admin Department: \n{lnd_team['team_id']}: {lnd_team['team_name']}, Manager: {user_handler.get_user(lnd_team['manager_id']).name}, Team Number: {lnd_team['team_number']}")
    print(f"\nCreated Admin team under HR and Admin Department: \n{admin_team['team_id']}: {admin_team['team_name']}, Manager: {user_handler.get_user(admin_team['manager_id']).name}, Team Number: {admin_team['team_number']}")

    # Create HR members under HR team
    hr_create = [
        {"name": "Aisha Binte Rahman", "email": "aisha.rahman.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Alvin Koh", "email": "alvin.koh.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Amandeep Kaur", "email": "amandeep.kaur.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Amira Noor", "email": "amira.noor.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Anand Kumar", "email": "anand.kumar.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Angela Lee", "email": "angela.lee.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Azlan Bin Hassan", "email": "azlan.hassan.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Bala Reddy", "email": "bala.reddy.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Belinda Tan", "email": "belinda.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Bryan Chua", "email": "bryan.chua.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Cassandra Goh", "email": "cassandra.goh.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Cheryl Lim", "email": "cheryl.lim.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Daniel Yeo", "email": "daniel.yeo.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Deepika Raj", "email": "deepika.raj.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Diana Low", "email": "diana.low.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Elaine Teo", "email": "elaine.teo.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Farah Abdullah", "email": "farah.abdullah.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Faizal Bin Ahmad", "email": "faizal.ahmad.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Felicia Ng", "email": "felicia.ng.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Gavin Tan", "email": "gavin.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Geetha Menon", "email": "geetha.menon.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Grace Pang", "email": "grace.pang.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Hakim Bin Ismail", "email": "hakim.ismail.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Hannah Soh", "email": "hannah.soh.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Harini Devi", "email": "harini.devi.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Imran Bin Yusof", "email": "imran.yusof.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Indra Nair", "email": "indra.nair.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Irene Chee", "email": "irene.chee.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Jasmine Lee", "email": "jasmine.lee.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Joel Ong", "email": "joel.ong.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Joshua Lim", "email": "joshua.lim.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Kavitha Raj", "email": "kavitha.raj.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Khairul Bin Omar", "email": "khairul.omar.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Kimberly Toh", "email": "kimberly.toh.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Lydia Yeo", "email": "lydia.yeo.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Manpreet Singh", "email": "manpreet.singh.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Melissa Ng", "email": "melissa.ng.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Muthu Raj", "email": "muthu.raj.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Nadiah Binte Ali", "email": "nadiah.ali.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Nurul Ain", "email": "nurul.ain.hr@kira.ai", "password": "Password123!", "role": UserRole.HR, "admin": False, "department_id": departments[4]['department_id']},
    ]
    hr_members = []
    for user_data in hr_create:
        user = user_handler.create_user(**user_data)
        hr_members.append(user)
        department_handler.assign_user_to_team(
            team_id=hr_team['team_id'],
            user_id=user.user_id,
            manager_id=hr_team['manager_id']
        )

    # Create L&D members under L&D team
    lnd_create = [
        {"name": "Adam Koh", "email": "adam.koh.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Afiq Bin Noor", "email": "afiq.noor.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Alicia Goh", "email": "alicia.goh.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Anita Tan", "email": "anita.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Arun Raj", "email": "arun.raj.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Azhar Bin Hamid", "email": "azhar.hamid.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Beatrice Lee", "email": "beatrice.lee.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Benedict Ong", "email": "benedict.ong.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Carmen Chua", "email": "carmen.chua.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Charles Tan", "email": "charles.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Darren Lim", "email": "darren.lim.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Deborah Goh", "email": "deborah.goh.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Dev Anand", "email": "dev.anand.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Diana Ng", "email": "diana.ng.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Eliza Tan", "email": "eliza.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Faiz Bin Karim", "email": "faiz.karim.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Faridah Binte Hassan", "email": "faridah.hassan.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Gurpreet Singh", "email": "gurpreet.singh.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Hui Ling", "email": "hui.ling.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
        {"name": "Iskandar Bin Ali", "email": "iskandar.ali.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[4]['department_id']},
    ]
    lnd_members = []
    for user_data in lnd_create:
        user = user_handler.create_user(**user_data)
        lnd_members.append(user)
        department_handler.assign_user_to_team(
            team_id=lnd_team['team_id'],
            user_id=user.user_id,
            manager_id=lnd_team['manager_id']
        )
    
    # Create Admin members under Admin team
    admin_create = [
        {"name": "Adeline Tan", "email": "adeline.tan.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Ahmad Fauzi", "email": "ahmad.fauzi.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Amrit Kaur", "email": "amrit.kaur.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Benjamin Lim", "email": "benjamin.lim.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Cynthia Goh", "email": "cynthia.goh.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "David Ong", "email": "david.ong.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Farhana Binte Ismail", "email": "farhana.ismail.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Ganesh Raj", "email": "ganesh.raj.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Hazirah Noor", "email": "hazirah.noor.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
        {"name": "Joanne Lee", "email": "joanne.lee.hr@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": True, "department_id": departments[4]['department_id']},
    ]
    admin_members = []
    for user_data in admin_create:
        user = user_handler.create_user(**user_data)
        admin_members.append(user)
        department_handler.assign_user_to_team(
            team_id=admin_team['team_id'],
            user_id=user.user_id,
            manager_id=admin_team['manager_id']
        )
    
    print(f"\nCreated {len(hr_members)} HR users and assigned to HR and Admin Team.")
    team_users = department_handler.get_users_in_team(hr_team['team_id'])
    print(f"\nTeam {hr_team['team_name']} ({hr_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    print(f"\nCreated {len(lnd_members)} L&D users and assigned to HR and Admin Team.")
    team_users = department_handler.get_users_in_team(lnd_team['team_id'])
    print(f"\nTeam {lnd_team['team_name']} ({lnd_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    print(f"\nCreated {len(admin_members)} Admin users and assigned to HR and Admin Team.")
    team_users = department_handler.get_users_in_team(admin_team['team_id'])
    print(f"\nTeam {admin_team['team_name']} ({admin_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")

    print("\n" + "=" * 60)


    # Create Finance Manager Team under Finance Department
    finance_manager_team = department_handler.create_team_under_department(department_id=departments[5]['department_id'], team_name="Finance Manager", manager_id=directors[5].user_id)

    # Finance Team Managers
    finance_users_create = [
        {"name": "Ivan Lee", "email": "ivan.lee.fin@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jasmine Koh", "email": "jasmine.koh.fin@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Karthik Raj", "email": "karthik.raj.fin@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Liyana Binte Hassan", "email": "liyana.hassan.fin@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Marcus Tan", "email": "marcus.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.MANAGER, "admin": False, "department_id": departments[5]['department_id']},
    ]
    finance_managers = []
    for user_data in finance_users_create:
        user = user_handler.create_user(**user_data)
        finance_managers.append(user)
        department_handler.assign_user_to_team(team_id=finance_manager_team['team_id'], user_id=user.user_id, manager_id=finance_manager_team['manager_id'])
    
    print(f"\nCreated {len(finance_users_create)} finance team managers.")
    for user in finance_managers:
        print(f"{user.user_id}: {user.name}, {user.email}, {department_handler.view_department_by_id(user.department_id)['department_name']}, Assigned to Team: {finance_manager_team['team_number']}, Manager: {user_handler.get_user(finance_manager_team['manager_id']).name}")
    
    print("\n" + "=" * 60)

    # Create Finance Executive team under Finance Manager Team
    finance_teams_create = [
        {"team_name": "Accounts Payable Team", "manager_id": finance_managers[0].user_id},
        {"team_name": "Accounts Receivable Team", "manager_id": finance_managers[1].user_id},
        {"team_name": "Payroll Team", "manager_id": finance_managers[2].user_id},
        {"team_name": "Budgeting Team", "manager_id": finance_managers[3].user_id},
        {"team_name": "Financial Reporting Team", "manager_id": finance_managers[4].user_id},
    ]

    finance_teams = []
    for team_data in finance_teams_create:
        team = department_handler.create_team_under_team(
            team_id=finance_manager_team['team_id'],
            team_name=team_data['team_name'],
            manager_id=team_data['manager_id']
        )
        finance_teams.append(team)

    print(f"\nCreated {len(finance_teams_create)} finance executive teams under Finance Manager Team.")
    for team in finance_teams:
        print(f"{team['team_id']}: {team['team_name']}, Manager: {user_handler.get_user(team['manager_id']).name}, Team Number: {team['team_number']}")

    # Create Finance Execs under Finance Exec team
    finance_execs_create = [
        {"name": "Abdul Malik", "email": "abdul.malik.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Adeline Ng", "email": "adeline.ng.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Aisha Binte Ahmad", "email": "aisha.ahmad.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Alex Tan", "email": "alex.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Alicia Wong", "email": "alicia.wong.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Amy Toh", "email": "amy.toh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Andrew Lee", "email": "andrew.lee.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Angeline Koh", "email": "angeline.koh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Benjamin Ong", "email": "benjamin.ong.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Bernice Tan", "email": "bernice.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Bryan Chia", "email": "bryan.chia.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Carmen Yeo", "email": "carmen.yeo.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Cheryl Tan", "email": "cheryl.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Daniel Goh", "email": "daniel.goh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Daphne Lee", "email": "daphne.lee.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Deepak Raj", "email": "deepak.raj.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Denise Lim", "email": "denise.lim.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Derrick Koh", "email": "derrick.koh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Elaine Goh", "email": "elaine.goh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Eugene Tan", "email": "eugene.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Farid Bin Noor", "email": "farid.noor.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Farzana Binte Ahmad", "email": "farzana.ahmad.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Felicia Lee", "email": "felicia.lee.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Gavin Ng", "email": "gavin.ng.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Grace Wong", "email": "grace.wong.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Hafiz Bin Ali", "email": "hafiz.ali.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Harpreet Singh", "email": "harpreet.singh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Hazirah Noor", "email": "hazirah.noor.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Ian Koh", "email": "ian.koh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Irene Tan", "email": "irene.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Ismail Bin Hassan", "email": "ismail.hassan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jackie Ong", "email": "jackie.ong.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Janice Chua", "email": "janice.chua.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jason Lim", "email": "jason.lim.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jennifer Goh", "email": "jennifer.goh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jeremy Tan", "email": "jeremy.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Joanne Low", "email": "joanne.low.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Joel Ng", "email": "joel.ng.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jonathan Chia", "email": "jonathan.chia.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Jordana Tan", "email": "jordana.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Kelvin Goh", "email": "kelvin.goh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Kenneth Ong", "email": "kenneth.ong.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Krishnan Iyer", "email": "krishnan.iyer.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Laila Binte Osman", "email": "laila.osman.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Lawrence Tan", "email": "lawrence.tan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Liang Wei", "email": "liang.wei.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Melissa Koh", "email": "melissa.koh.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Mohammad Rizwan", "email": "mohammad.rizwan.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Natalie Ng", "email": "natalie.ng.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
        {"name": "Neha Rani", "email": "neha.rani.fin@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[5]['department_id']},
    ]
    finance_execs = []
    for user_data in finance_execs_create:
        user = user_handler.create_user(**user_data)
        finance_execs.append(user)
        team_index = finance_execs_create.index(user_data) % len(finance_teams)
        department_handler.assign_user_to_team(
            team_id=finance_teams[team_index]['team_id'],
            user_id=user.user_id,
            manager_id=finance_teams[team_index]['manager_id']
        )

    print(f"\nCreated {len(finance_execs_create)} finance executive users and assigned to Finance executive teams.")
    for team in finance_teams:
        team_users = department_handler.get_users_in_team(team['team_id'])
        print(f"\nTeam {team['team_name']} ({team['team_number']}) Members:")
        for u in team_users:
            print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    print("\n" + "=" * 60)

    # Create IT team under IT department
    it_team = department_handler.create_team_under_department(
        department_id=departments[6]['department_id'],
        team_name="IT Team",
        manager_id=directors[6].user_id
    )
    print(f"\nCreated IT Team under IT Department: \n{it_team['team_id']}: {it_team['team_name']}, Manager: {user_handler.get_user(it_team['manager_id']).name}, Team Number: {it_team['team_number']}")

    # Create IT members under IT Team
    it_create = [
        {"name": "Aaron Koh", "email": "aaron.koh.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Abdul Rahim", "email": "abdul.rahim.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Aileen Tan", "email": "aileen.tan.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Alex Lim", "email": "alex.lim.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Alicia Ng", "email": "alicia.ng.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Amarjit Singh", "email": "amarjit.singh.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Amy Wong", "email": "amy.wong.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Anand Krishnan", "email": "anand.krishnan.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Angela Lee", "email": "angela.lee.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Benjamin Toh", "email": "benjamin.toh.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Bryan Tan", "email": "bryan.tan.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Cassandra Yeo", "email": "cassandra.yeo.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Celine Koh", "email": "celine.koh.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Cheng Wei", "email": "cheng.wei.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Daniel Ong", "email": "daniel.ong.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Deepa Rani", "email": "deepa.rani.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Derrick Lim", "email": "derrick.lim.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Elaine Chua", "email": "elaine.chua.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Eugene Lee", "email": "eugene.lee.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Farid Bin Omar", "email": "farid.omar.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Farzana Binte Ali", "email": "farzana.ali.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Gavin Tan", "email": "gavin.tan.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Geetha Menon", "email": "geetha.menon.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Grace Koh", "email": "grace.koh.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Hakim Ismail", "email": "hakim.ismail.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Harpreet Kaur", "email": "harpreet.kaur.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Hui Min", "email": "hui.min.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Ian Ng", "email": "ian.ng.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Indra Raj", "email": "indra.raj.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
        {"name": "Iskandar Bin Noor", "email": "iskandar.noor.it@kira.ai", "password": "Password123!", "role": UserRole.STAFF, "admin": False, "department_id": departments[6]['department_id']},
    ]
    it_members = []
    for user_data in it_create:
        user = user_handler.create_user(**user_data)
        it_members.append(user)
        department_handler.assign_user_to_team(
            team_id=it_team['team_id'],
            user_id=user.user_id,
            manager_id=it_team['manager_id']
        )
    print(f"\nCreated {len(it_members)} IT users and assigned to IT Support Team.")
    team_users = department_handler.get_users_in_team(it_team['team_id'])
    print(f"\nTeam {it_team['team_name']} ({it_team['team_number']}) Members:")
    for u in team_users:
        print(f"{u['user_id']}: {user_handler.get_user(u['user_id']).name}, {user_handler.get_user(u['user_id']).email}, {department_handler.view_department_by_id(user_handler.get_user(u['user_id']).department_id)['department_name']}")
    
    print("\n" + "=" * 60)


    # =================================================


    # Create Project 

    director_project_data = [
        {"project_name": "Sales Automation Tool", "project_manager_id": directors[0].user_id},
        {"project_name": "Consulting CRM System", "project_manager_id": directors[1].user_id},
        {"project_name": "Software Solutions Development", "project_manager_id": directors[2].user_id},
        {"project_name": "Enterprise Operations Dashboard", "project_manager_id": directors[3].user_id},
        {"project_name": "HR Management Platform", "project_manager_id": directors[4].user_id},
        {"project_name": "Financial Analytics Suite", "project_manager_id": directors[5].user_id},
        {"project_name": "IT Infrastructure Upgrade", "project_manager_id": directors[6].user_id},
    ]

    sales_project_data = [
        {"project_name": "Client Acquisition Campaign", "project_manager_id": sales_managers[0].user_id},
        {"project_name": "Market Expansion Strategy", "project_manager_id": sales_managers[1].user_id},
        {"project_name": "Sales Training Program", "project_manager_id": sales_managers[2].user_id},
        {"project_name": "Product Launch Event", "project_manager_id": sales_managers[3].user_id},
        {"project_name": "Customer Retention Initiative", "project_manager_id": sales_managers[4].user_id},
    ]

    finance_project_data = [
        {"project_name": "Budget Planning Tool", "project_manager_id": finance_managers[0].user_id},
        {"project_name": "Expense Tracking System", "project_manager_id": finance_managers[1].user_id},
        {"project_name": "Payroll Automation", "project_manager_id": finance_managers[2].user_id},
        {"project_name": "Financial Reporting Dashboard", "project_manager_id": finance_managers[3].user_id},
        {"project_name": "Audit Compliance System", "project_manager_id": finance_managers[4].user_id},
    ]

    # Create projects for Directors
    director_projects = []
    for project_data in director_project_data:
        project = project_handler.create_project(**project_data)
        director_projects.append(project)
        print(f"\nCreated Project: {project['project_id']}: {project['project_name']}, Managed by: {user_handler.get_user(project['project_manager']).name}")

    # Create projects for Sales Managers
    sales_projects = []
    for project_data in sales_project_data:
        project = project_handler.create_project(**project_data)
        sales_projects.append(project)
        print(f"\nCreated Project: {project['project_id']}: {project['project_name']}, Managed by: {user_handler.get_user(project['project_manager']).name}")

    # Create projects for Finance Managers
    finance_projects = []
    for project_data in finance_project_data:
        project = project_handler.create_project(**project_data)
        finance_projects.append(project)
        print(f"\nCreated Project: {project['project_id']}: {project['project_name']}, Managed by: {user_handler.get_user(project['project_manager']).name}")

    print(f"\nCreated a total of {len(director_projects) + len(sales_projects) + len(finance_projects)} projects.\n")
    for director in directors:
        projects = project_handler.get_projects_by_manager(director.user_id)
        for project in projects:
            print(f"Project {project['project_name']} created under Director {director.name}.")
    for manager in sales_managers:
        projects = project_handler.get_projects_by_manager(manager.user_id)
        for project in projects:
            print(f"Project {project['project_name']} created under Sales Manager {manager.name}.")
    for manager in finance_managers:
        projects = project_handler.get_projects_by_manager(manager.user_id)
        for project in projects:
            print(f"Project {project['project_name']} created under Finance Manager {manager.name}.")
    print("\n" + "=" * 60)

    # Create task for sales managers
    sales_manager_task = task_handler.create_task(**{"title": "Sales Strategy Development", "description": "Develop a comprehensive sales strategy for the upcoming quarter.", "start_date": date(2025, 11, 9), "deadline": date(2025, 11, 10), "priority": 4, "tag": "Sales", "project_id": 1, "recurring": 1, "creator_id": sales_managers[0].user_id})

    sales_managers_ids = []
    for manager in sales_managers:
        sales_managers_ids.append(manager.user_id)
    
    task_assignment_handler.assign_users(sales_manager_task.id, sales_managers_ids)
    comment_handler.add_comment(task_id=sales_manager_task.id, user_id=sales_managers[0].user_id, comment_text="Please ensure the strategy aligns with our overall business goals.")
    print(f"\nCreated Task {sales_manager_task.id}: Assigned Task '{sales_manager_task.title}' to Sales Managers: {', '.join([user_handler.get_user(uid).name for uid in sales_managers_ids])}")

    # Create task for account managers
    account_manager_task = task_handler.create_task(**{"title": "Account Management Strategy", "description": "Develop a strategy for managing key accounts.", "start_date": date(2025, 11, 7), "deadline": date(2025, 11, 9), "priority": 5, "tag": "Accounts", "project_id": 8, "creator_id": account_managers[0].user_id})

    account_managers_ids = []
    for manager in account_managers:
        account_managers_ids.append(manager.user_id)

    task_assignment_handler.assign_users(account_manager_task.id, account_managers_ids)
    comment_handler.add_comment(task_id=account_manager_task.id, user_id=account_managers[0].user_id, comment_text="Focus on high-value clients for this strategy.")
    print(f"\nCreated Task {account_manager_task.id}: Assigned Task '{account_manager_task.title}' to Account Managers: {', '.join([user_handler.get_user(uid).name for uid in account_managers_ids])}")

    # Create tasks for consultants
    consultant_task = task_handler.create_task(**{"title": "Requirement Gathering", "description": "Collect all necessary requirements from stakeholders.", "start_date": date(2025, 11, 7), "deadline": date(2025, 11, 11), "priority": 5, "tag": "Consulting", "project_id": 2, "creator_id": consultants[0].user_id})
    consultants_ids = []
    for consultant in consultants:
        consultants_ids.append(consultant.user_id)

    task_assignment_handler.assign_users(consultant_task.id, consultants_ids)
    comment_handler.add_comment(task_id=consultant_task.id, user_id=consultants[0].user_id, comment_text="Ensure all requirements are gathered before the deadline.")
    print(f"\nCreated Task {consultant_task.id}: Assigned Task '{consultant_task.title}' to Consultants: {', '.join([user_handler.get_user(uid).name for uid in consultants_ids])}")

    # Create tasks for developers
    developer_task = task_handler.create_task(**{"title": "System Architecture Design", "description": "Design the architecture for the new software solution.", "start_date": date(2025, 11, 10), "deadline": date(2025, 11, 20), "priority": 3, "tag": "Development", "project_id": 3, "creator_id": developers[0].user_id})
    developers_ids = []
    for developer in developers:
        developers_ids.append(developer.user_id)

    task_assignment_handler.assign_users(developer_task.id, developers_ids)
    comment_handler.add_comment(task_id=developer_task.id, user_id=developers[0].user_id, comment_text="Design the system with scalability in mind.")
    print(f"\nCreated Task {developer_task.id}: Assigned Task '{developer_task.title}' to Developers: {', '.join([user_handler.get_user(uid).name for uid in developers_ids])}")

    # Create tasks for support users
    support_user_task = task_handler.create_task(**{"title": "Customer Support Ticket Resolution", "description": "Resolve customer support tickets in a timely manner.", "start_date": date(2025, 11, 5), "deadline": date(2025, 11, 12), "priority": 3, "tag": "Support", "project_id": 3, "creator_id": support_users[0].user_id})
    support_users_ids = []
    for support_user in support_users:
        support_users_ids.append(support_user.user_id)

    task_assignment_handler.assign_users(support_user_task.id, support_users_ids)
    comment_handler.add_comment(task_id=support_user_task.id, user_id=support_users[0].user_id, comment_text="Prioritize urgent tickets and keep customers updated.")
    print(f"\nCreated Task {support_user_task.id}: Assigned Task '{support_user_task.title}' to Support Users: {', '.join([user_handler.get_user(uid).name for uid in support_users_ids])}")

    # Create tasks for senior engineers
    senior_engineer_task = task_handler.create_task(**{"title": "Operational Workflow Analysis", "description": "Analyze current workflows to identify improvement areas.", "start_date": date(2025, 11, 5), "deadline": date(2025, 11, 12), "priority": 4, "tag": "Operations", "project_id": 4, "creator_id": senior_engineers[0].user_id})
    senior_engineers_ids = []
    for senior_engineer in senior_engineers:
        senior_engineers_ids.append(senior_engineer.user_id)

    task_assignment_handler.assign_users(senior_engineer_task.id, senior_engineers_ids)
    comment_handler.add_comment(task_id=senior_engineer_task.id, user_id=senior_engineers[0].user_id, comment_text="Identify key bottlenecks and propose solutions.")
    print(f"\nCreated Task {senior_engineer_task.id}: Assigned Task '{senior_engineer_task.title}' to Senior Engineers: {', '.join([user_handler.get_user(uid).name for uid in senior_engineers_ids])}")

    # Create tasks for junior engineers
    junior_engineer_task = task_handler.create_task(**{"title": "System Testing and QA", "description": "Conduct system testing and quality assurance for new software solutions.", "start_date": date(2025, 11, 10), "deadline": date(2025, 11, 18), "priority": 3, "tag": "Engineering", "project_id": 4, "creator_id": junior_engineers[0].user_id})
    junior_engineers_ids = []
    for junior_engineer in junior_engineers:
        junior_engineers_ids.append(junior_engineer.user_id)

    task_assignment_handler.assign_users(junior_engineer_task.id, junior_engineers_ids)
    comment_handler.add_comment(task_id=junior_engineer_task.id, user_id=junior_engineers[0].user_id, comment_text="Ensure thorough testing and documentation.")
    print(f"\nCreated Task {junior_engineer_task.id}: Assigned Task '{junior_engineer_task.title}' to Junior Engineers: {', '.join([user_handler.get_user(uid).name for uid in junior_engineers_ids])}")

    # Create tasks for call center members
    call_centre_member_task = task_handler.create_task(**{"title": "Customer Interaction Management", "description": "Manage customer interactions and provide support.", "start_date": date(2025, 11, 6), "deadline": date(2025, 11, 13), "priority": 4, "tag": "Call Center", "project_id": 4, "creator_id": call_centre_members[0].user_id})
    call_centre_members_ids = []
    for call_centre_member in call_centre_members:
        call_centre_members_ids.append(call_centre_member.user_id)

    task_assignment_handler.assign_users(call_centre_member_task.id, call_centre_members_ids)
    comment_handler.add_comment(task_id=call_centre_member_task.id, user_id=call_centre_members[0].user_id, comment_text="Ensure all customer interactions are logged.")
    print(f"\nCreated Task {call_centre_member_task.id}: Assigned Task '{call_centre_member_task.title}' to Call Centre Members: {', '.join([user_handler.get_user(uid).name for uid in call_centre_members_ids])}")

    # Create tasks for operation planning members
    operation_planning_member_task = task_handler.create_task(**{"title": "Operational Planning and Coordination", "description": "Plan and coordinate operational activities for efficiency.", "start_date": date(2025, 11, 5), "deadline": date(2025, 11, 12), "priority": 4, "tag": "Operations", "project_id": 4, "creator_id": operation_planning_members[0].user_id})
    operation_planning_members_ids = []
    for operation_planning_member in operation_planning_members:
        operation_planning_members_ids.append(operation_planning_member.user_id)

    task_assignment_handler.assign_users(operation_planning_member_task.id, operation_planning_members_ids)
    comment_handler.add_comment(task_id=operation_planning_member_task.id, user_id=operation_planning_members[0].user_id, comment_text="Ensure all operational plans are documented.")
    print(f"\nCreated Task {operation_planning_member_task.id}: Assigned Task '{operation_planning_member_task.title}' to Operation Planning Members: {', '.join([user_handler.get_user(uid).name for uid in operation_planning_members_ids])}")

    # Create tasks for HR members
    hr_member_task = task_handler.create_task(**{"title": "Employee Onboarding Process", "description": "Create a streamlined onboarding process for new hires.", "start_date": date(2025, 11, 9), "deadline": date(2025, 11, 10), "priority": 5, "tag": "HR", "project_id": 5, "creator_id": hr_members[0].user_id})
    hr_members_ids = []
    for hr_member in hr_members:
        hr_members_ids.append(hr_member.user_id)

    task_assignment_handler.assign_users(hr_member_task.id, hr_members_ids)
    comment_handler.add_comment(task_id=hr_member_task.id, user_id=hr_members[0].user_id, comment_text="Ensure a smooth onboarding experience for new hires.")
    print(f"\nCreated Task {hr_member_task.id}: Assigned Task '{hr_member_task.title}' to HR Members: {', '.join([user_handler.get_user(uid).name for uid in hr_members_ids])}")

    # Create tasks for L&D members
    lnd_member_task = task_handler.create_task(**{"title": "Learning and Development Programs", "description": "Design and implement learning and development programs for employees.", "start_date": date(2025, 11, 8), "deadline": date(2025, 11, 14), "priority": 4, "tag": "L&D", "project_id": 5, "creator_id": lnd_members[0].user_id})
    lnd_members_ids = []
    for lnd_member in lnd_members:
        lnd_members_ids.append(lnd_member.user_id)

    task_assignment_handler.assign_users(lnd_member_task.id, lnd_members_ids)
    comment_handler.add_comment(task_id=lnd_member_task.id, user_id=lnd_members[0].user_id, comment_text="Ensure all training materials are up-to-date.")
    print(f"\nCreated Task {lnd_member_task.id}: Assigned Task '{lnd_member_task.title}' to L&D Members: {', '.join([user_handler.get_user(uid).name for uid in lnd_members_ids])}")

    # Create tasks for admin members
    admin_member_task = task_handler.create_task(**{"title": "Administrative Support Tasks", "description": "Handle various administrative support tasks for the organization.", "start_date": date(2025, 11, 7), "deadline": date(2025, 11, 13), "priority": 3, "tag": "Admin", "project_id": 5, "creator_id": admin_members[0].user_id})
    admin_members_ids = []
    for admin_member in admin_members:
        admin_members_ids.append(admin_member.user_id)

    task_assignment_handler.assign_users(admin_member_task.id, admin_members_ids)
    comment_handler.add_comment(task_id=admin_member_task.id, user_id=admin_members[0].user_id, comment_text="Ensure all administrative tasks are prioritized.")
    print(f"\nCreated Task {admin_member_task.id}: Assigned Task '{admin_member_task.title}' to Admin Members: {', '.join([user_handler.get_user(uid).name for uid in admin_members_ids])}")

    # Create tasks for finance managers
    finance_manager_task = task_handler.create_task(**{"title": "Financial Data Analysis", "description": "Analyze financial data to identify trends and insights.", "start_date": date(2025, 11, 6), "deadline": date(2025, 11, 13), "priority": 4, "tag": "Finance", "project_id": 6, "creator_id": finance_managers[0].user_id})
    finance_managers_ids = []
    for finance_manager in finance_managers:
        finance_managers_ids.append(finance_manager.user_id)

    task_assignment_handler.assign_users(finance_manager_task.id, finance_managers_ids)
    comment_handler.add_comment(task_id=finance_manager_task.id, user_id=finance_managers[0].user_id, comment_text="Focus on high-value clients for this strategy.")
    print(f"\nCreated Task {finance_manager_task.id}: Assigned Task '{finance_manager_task.title}' to Finance Managers: {', '.join([user_handler.get_user(uid).name for uid in finance_managers_ids])}")

    # Create tasks for finance executives
    finance_exec_task = task_handler.create_task(**{"title": "Expense Report Preparation", "description": "Prepare and review expense reports for accuracy.", "start_date": date(2025, 11, 6), "deadline": date(2025, 11, 12), "priority": 4, "tag": "Finance", "project_id": 13, "creator_id": finance_execs[0].user_id})
    finance_execs_ids = []
    for finance_exec in finance_execs:
        finance_execs_ids.append(finance_exec.user_id)

    task_assignment_handler.assign_users(finance_exec_task.id, finance_execs_ids)
    comment_handler.add_comment(task_id=finance_exec_task.id, user_id=finance_execs[0].user_id, comment_text="Ensure all expense reports comply with company policies.")
    print(f"\nCreated Task {finance_exec_task.id}: Assigned Task '{finance_exec_task.title}' to Finance Executives: {', '.join([user_handler.get_user(uid).name for uid in finance_execs_ids])}")

    # Create tasks for IT members
    it_member_task = task_handler.create_task(**{"title": "Network Infrastructure Upgrade", "description": "Upgrade the existing network infrastructure for better performance.", "start_date": date(2025, 11, 11), "deadline": date(2025, 11, 18), "priority": 3, "tag": "IT", "project_id": 7, "creator_id": it_members[0].user_id})
    it_members_ids = []
    for it_member in it_members:
        it_members_ids.append(it_member.user_id)

    task_assignment_handler.assign_users(it_member_task.id, it_members_ids)
    comment_handler.add_comment(task_id=it_member_task.id, user_id=it_members[0].user_id, comment_text="Coordinate with all teams to minimize downtime during the upgrade.")
    print(f"Created Task {it_member_task.id}: Assigned Task '{it_member_task.title}' to IT Members: {', '.join([user_handler.get_user(uid).name for uid in it_members_ids])}")


if __name__ == "__main__":
    
    seed_database()