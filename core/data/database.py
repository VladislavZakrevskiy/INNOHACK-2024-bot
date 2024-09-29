import psycopg2
import datetime



class DataBase():
    def __init__(self, host, user, password, user_db, project_db, port) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.user_db = user_db
        self.project_db = project_db
        self.port = port
        self.data = []
        self.data_check_hour = 10
        self.data_check_minute = 5
        self.data_check_count = 1
        self.data_time_to_end = 36

    async def connect_user(self):
        user_connection = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.user_db,
            port=self.port
        )
        return user_connection
    
    async def connect_project(self):
        user_connection = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.project_db,
            port=self.port
        )
        return user_connection
    
    async def disconnect(self, connection):
        connection.close()
        print("[INFO] PostgreSQL connection closed")

    async def update_tasks_data(self, telegram_id, users_connection, projects_connection):
        self.data = []
        with users_connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, full_name FROM users WHERE telegram_id = %s;""", (telegram_id,)
            )
            (user_id, user_fullname) = cursor.fetchone()

        with projects_connection.cursor() as cursor:

            # получение задач
            cursor.execute(
                """SELECT id, owner_id, create_date, deadline_date, description, title, status_id FROM task WHERE executor_id = %s;""", (user_id,)
            )
            tasks = cursor.fetchall()

            # получение информации о каждой задаче

            for task in tasks:
                (task_id, task_owner_id, task_create_date, task_deadline_date, task_description, task_title, task_status_id) = task
                if task_deadline_date != None:
                    day = task_deadline_date.date().day
                    month = task_deadline_date.date().month
                    hour = task_deadline_date.time().hour
                    minute = task_deadline_date.time().minute
                    day_left = (task_deadline_date - datetime.datetime.now()).days
                else:
                    day_left = "None"
                    task_create_date, day, month, hour, minute, = 0, 0, 0, 0, 0
                #получение информации о статусе задачи

                cursor.execute(
                """SELECT name, space_id FROM status WHERE id = %s;""", (task_status_id,)
                )
                (status_name, space_id) = cursor.fetchone()

                #получение информации о space, в котором лежит задача

                cursor.execute(
                """SELECT owner_id, description, name, project_id FROM space WHERE id = %s;""", (space_id,)
                )
                (space_owner_id, space_description, space_name, project_id) = cursor.fetchone()

                # получение информации о проекте, в котором находится space

                cursor.execute(
                """SELECT owner_id, description, name FROM project WHERE id = %s;""", (project_id,)
                )
                (project_owner_id, project_description, project_name) = cursor.fetchone()

                #USER DATABASE Получение имен владельцев

                with users_connection.cursor() as users_cursor:
                    users_cursor.execute(
                    """SELECT full_name FROM users WHERE id = %s;""", (task_owner_id,)
                    )
                    task_owner_fullname = users_cursor.fetchone()
                    users_cursor.execute(
                    """SELECT full_name FROM users WHERE id = %s;""", (space_owner_id,)
                    )
                    space_owner_fullname = users_cursor.fetchone()
                    users_cursor.execute(
                    """SELECT full_name FROM users WHERE id = %s;""", (project_owner_id,)
                    )
                    project_owner_fullname = users_cursor.fetchone()

                    # запаковываем всю информацию о задаче
                    project_image = None
                    self.data.append((
                        user_fullname,
                        ((task_create_date, day, month, hour, minute, task_deadline_date, day_left), task_title, task_owner_fullname, task_description, task_id),
                        (status_name),
                        (space_name, space_owner_fullname, space_description),
                        (project_name, project_image, project_owner_fullname, project_description)
                        
                        ))
        

    async def get_user(self, telegram_id, connection):
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT username, full_name FROM users WHERE telegram_id = %s;""", (telegram_id,)
            )
            (username, fullname) = cursor.fetchone()
        return username, fullname

    async def update_user(self, username, telegram_id, connection):
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT username FROM users WHERE telegram_id = %s;""", (telegram_id,)
            )
            old_id = cursor.fetchone()
            print(old_id)
            if old_id == None:
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE username = %s""", (telegram_id, username,)
                )
            else:
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE telegram_id = %s""", (None, telegram_id,)
                )
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE username = %s""", (telegram_id, username,)
                )
        connection.close()