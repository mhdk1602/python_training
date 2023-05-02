<h2>Exercise 1: Design a Simple ER Diagram</h2>

Consider an online bookstore application. The main entities are <strong>Author</strong>, <strong>Book</strong>, and <strong>Category</strong>. The application needs to store the following information:

<ul>
  <li><strong>Author:</strong> id, first name, last name, and date of birth</li>
  <li><strong>Book:</strong> id, title, publication date, price, and author</li>
  <li><strong>Category:</strong> id and name</li>
</ul>
Design an Entity-Relationship (ER) diagram for this application. Identify the primary keys and relationships between the entities. Consider the following constraints:

<ol>
  <li>A book must have exactly one author, but an author can write multiple books.</li>
  <li>A book can belong to one or more categories, and a category can have multiple books.</li>
</ol>&nbsp;

<details>
  <summary><strong>View answer</strong></summary>
Answer to Exercise 1
For the given exercise, the ER diagram would have the following entities and relationships:

Entities:
Author: id (primary key), first_name, last_name, date_of_birth
Book: id (primary key), title, publication_date, price, author_id (foreign key)
Category: id (primary key), name
Book_Category: book_id (foreign key), category_id (foreign key) [This is a junction table to store the many-to-many relationship between books and categories]
Relationships:
Author (1) --- (M) Book: One-to-many relationship between Author and Book, with the foreign key author_id in the Book table.
Book (M) --- (M) Category: Many-to-many relationship between Book and Category, represented by the junction table Book_Category, which has foreign keys book_id and category_id.
</details>