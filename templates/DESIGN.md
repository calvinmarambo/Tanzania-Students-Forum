CS50 Final project: Tanzania Students Forum
============

Programming languages used: Python, SQL, Javascript and html

Files: application.py, helpers.py, Static (scripts.js and style.css) and Templates (12 html templates decribed below), forum.db


Design decisions and functionalities:
Login page: Decided to have register, login and change password on the navigation bar; login and register on the right and change
            password on the left. These designs were implemented in layout.html

            * Register:Uses a form to get a username, schoolname and password. Used SQL to insert these values if username is not taken
            * Login: Uses a form to get a username and password. Used SQL to check if username is exists and password is correct.
            * Changepassword:Uses a form to get the username 2 passwords. Used SQL to check if username is correct and also check if
            the two passwords match. If they do, SQL updates the password in the database.


Index page: This functions as the homepage. Used jinja to implement welcome greeting at the top.
            Also decided to display the users own questions ordered by time (most recent first).
            This would make it easier for users to navigate through their own questions and see the responses/comments.

Askquestions: Used SQL to get questions & category and inserted these on the questions table in the database. Also decided
            to get the most recent asked questions (SQL Ordered by time limited to 10).
            In the html, is a form to get the question and category and an "Add Questions" button.

Explore: Used SQL to display all the questions from the database. Decided to create a link to the questions which would be
        clickable and would direct the user to the questionbank.html.
        In questionsbank.html, I used jinja to display each question asked.

Search: Used a form to get the text inputted. Split this text into keywords and used an SQL command to search on the database
        for questions or categories LIKE the keywords. Removed duplicates and found the number of similarities in common.
        Counted these similarities and sorted them first before being displayed in questionsbank.html

Analytics: Used SQL to query the database for a count of all questions grouped by user_id. Return a JSON array of these.
            Using javascript (found script.js), I implemented D3 data visualization where I plotted a bar graph with
            username on the x-axis and question_count on the y-axis.
            Used display.html to display this graph

Edit:Used SQLs to UPDATE command to update questions when an owner of the question clicks the edit button. Users will be taken
        to the edit.html page where they can input an edit on a form and submit it.

Question: Questions are clickable (created a link to each question). On clicking a specific question, users are redirected to comments page where
        exists a form to submit comments. These get posted on the top of the page.



