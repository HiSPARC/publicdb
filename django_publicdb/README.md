URL scheme for detector positions
=================================

	/detector_position
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
