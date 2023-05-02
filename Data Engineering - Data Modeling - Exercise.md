<h2>Exercise 1: Design a Simple ER Diagram</h2>
<p>Consider an online bookstore application. The main entities are <strong>Author</strong>, <strong>Book</strong>, and <strong>Category</strong>. The application needs to store the following information:</p>

<ul>
  <li>Author: id, first name, last name, and date of birth</li>
  <li>Book: id, title, publication date, price, and author</li>
  <li>Category: id and name</li>
</ul>

<p>Design an Entity-Relationship (ER) diagram for this application. Identify the primary keys and relationships between the entities. Consider the following constraints:</p>

<ol>
  <li>A book must have exactly one author, but an author can write multiple books.</li>
  <li>A book can belong to one or more categories, and a category can have multiple books.</li>
</ol>

<button id="button" onclick="toggle_visibility('answer')">View answer</button>
<div id="answer" style="display:none">
    <h2>Answer to Exercise 1</h2>
    <p>For the given exercise, the ER diagram would have the following entities and relationships:</p>
    <ul>
      <li>Entities:</li>
      <ul>
        <li>Author: id (primary key), first_name, last_name, date_of_birth</li>
        <li>Book: id (primary key), title, publication_date, price, author_id (foreign key)</li>
        <li>Category: id (primary key), name</li>
        <li>Book_Category: book_id (foreign key), category_id (foreign key) [This is a junction table to store the many-to-many relationship between books and categories]</li>
      </ul>
      <li>Relationships:</li>
      <ul>
        <li>Author (1) --- (M) Book: One-to-many relationship between Author and Book, with the foreign key <code>author_id</code> in the Book table.</li>
        <li>Book (M) --- (M) Category: Many-to-many relationship between Book and Category, represented by the junction table <code>Book_Category</code>, which has foreign keys <code>book_id</code> and <code>category_id</code>.</li>
      </ul>
    </ul>
</div>

<script type="text/javascript">
  function toggle_visibility(id) {
    var e = document.getElementById(id);
    if (e.style.display == 'block' || e.style.display=='')
      e.style.display = 'none';
    else
      e.style.display = 'block';
  }
</script>