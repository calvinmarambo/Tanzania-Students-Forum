CS50 Final project: Tanzania Students Forum
============

### Description ###
A Question & Answer platform meant for Tanzanian Highschool students to learn from each other.

Running: Start Flask’s built-in web server. i.e Use flask to run the web application.

### Usage ###
Upon running flask, click the link to the web app's login page.

At the login page, you can choose to login, register or change your password if already a user.
(To log in you can use a dummy username of "Calvin" and a password of "1")

Consequent to login, users are directed to the index/homepage page where they can see all the questions they've asked before.
A greeting appears at the top with bearing the user's name and their school name.

On this page, more functionalities appear on the the navigation bar:

Ask Question: On clicking this, the user is directed to a page where they can post their question and category.
              On this page is also a list of 10 most recently asked questions that the user can see.
              On submitting a question, the user will be directed to the index page (with their most recent question on the top)

Explore: On clicking this, the user will be taken to the Questions Bank which contains a list of all questions in the database
          arranged with the most recent first.
         Users can click on a question of interest and they'll be directed to a comments page where they could see resposes to
          those questions and post comments themselves.
         On this page, users can edit their own questions by clicking an edit button highlighted in blue.

Analytics:This displays users rank based on the number of questions they've asked. This would be an incentive to make users ask
        many questions and therefore expand the question database.

Search: Here, users can search for questions using keywords from the questions or their categories. The results from these are
        ranked based on importance. (Most significant results at the top).

Change password:This functionality is present before login and also on login where users can input their username and setup a new
                password. On submitting, the user is redirected to the login page.

Logout: Logs the user out and redirects them to the login page




