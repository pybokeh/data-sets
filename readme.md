# Repo containing sample data sets for your own personal projects

#### But why?
There are plenty of repos that provide data sets or links to sites that provide free data sets.  So why yet another one?  What will set this repo apart is it will not only show
you how to get the data sets, but also how to populate your own PostgreSQL database server with the data sets.  Which means, this repo will contain the necessary SQL scripts.
I've also included instructions on how to install and setup your PostgreSQL database server using either Docker or Windows for those who don't have access to Docker or don't want
to mess with Docker at the moment.

As a bonus, I will also provide Python jupyter notebooks that show how you can query the data sets using PySpark or Ibis framework.  Why?  Why not?  Sometimes, it is good once in
a while, to step away from SQL world and venture into the world of dataframe-based APIs.  For most cases, you'll want to stick with SQL, but sometimes, it is convenient to use a
dataframe API.  One such convenience is to be able to write/save a dataframe directly to the database without having to execute DDL statements (CREATE TABLE), especially if the
dataframe contains several columns.  Other conveniences such as being able to select columns by regex pattern or by data types, are also super nice since it would be difficult or
impossible to do using SQL.