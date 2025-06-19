>> ------ Windows ----------
>Running the server:
> 
> set FLASK_ENV=development
> 
> set FLASK_APP=main.py
> 
> flask run
> 
> --------- Mac -------------
> 
> export FLASK_ENV=development
> 
> export FLASK_APP=main.py
> 
> flask run
> 
> ----------- Server Error ---------
> 
> chrome://net-internals/#sockets
> 

> -------- After creating the model database -------
> 
> Run in the terminal ( in mac run python3, in windows run 'py')
> 
> from main import db, app
> 
> app.app_context().push()
> 
> db.create_all()

> you can see the database created inside the folder instances
> 
> run the terminal again
> 
> ------------- Use mysql instead of sqlite -----------
> 
> pip3 install mysql-connector
> 
> pip3 install mysql-connector-python
> 
> pip3 install mysql-connector-python
> 
> Create a python file "create_db_file.py"
> 
> ------------- Migrations -----------
> 
> In case you want to add few columns to the database run this:
> 
>> pip3 install Flask-Migrate
> 
> from flask_migrate import Migrate
>
> under  this line: db = SQLAlchemy(app)
> 
> migrate = Migrate(app, db)
> 
> In the terminal type:
>
> flask db init
> 
> flask db migrate -m 'initial migration'
> 
> flask db upgrade
> 
> run server and check
> 
>> NOTE:
> 
> Any time you want to make migrations just type:
> 
> flask db migrate -m "added something"
> 
> flask db upgrade


-------- NOTES ----------
> in case that you faced an error like this:
> sqlalchemy.exc.NoReferencedTableError: Foreign key associated 
> with column 'post_model.poster_id' 
> could not find table 'usersmodel' 
> with which to generate a foreign key to target column 'id'
> 
> In my case i have a "UsersModel" as a model for my database,
> in relationship the model will be like this:
> 
> new_field = db.Column(db.Integer, db.ForeignKey('users_model.id'))
> 
> So, Why users_model?
> 
> the reason is that the data is the tabel is containing two words:
> 
> Users and Model, in every word is uppercased, so, in the database,
> the table should be called like this:
> 
> db.ForeignKey('users_model.id')

