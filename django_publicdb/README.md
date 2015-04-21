URL scheme for detector positions
=================================

	/detector-position
			|
			|-----------> /submit: 		Create new station layout
			|
			|-----------> /submitted: 	Show summary and send email for confirmation
			|
			|-----------> /confirm: 	New station layout confirmed by applicant, 
			|							send email to cluser coordinator for reviewing
			|
			|-----------> /review: 		Cluster coordinator reviews new layout and either 
										approves or denies new layout. Applicant gets 
										email with outcome
										
South: Run migration after updating model
=========================================

First make a migration for the changes i.e. update the layout of your database (here we
use the `inforecords` app).

	$ ./manage.py schemamigration inforecords --auto

Now, apply it

	$ ./manage.py migrate inforecords
