## Repo containing sample data sets for your own personal projects

#### But why?
There are plenty of repos that provide data sets or links to sites that provide free data sets.  So why yet another one?  What will set this repo apart is it will not only show
you how to get the data sets, but also how to populate your own PostgreSQL database server with the data sets.  Which means, this repo will contain the necessary SQL scripts.
I've also included instructions on how to install and setup your PostgreSQL database server using either Docker or Windows for those who don't have access to Docker or don't want
to mess with Docker at the moment.  Why PostgreSQL?  It is free, is a full-fledged database server that has been around forever, and is relatively easy to install.  If you want
to use a different database, it is relatively easy to convert my SQL scripts to work with the database of your choice.  You'll have to figure out the difference in data types and
constraints.

As a bonus, I will also provide Python jupyter notebooks that show how you can query the data sets using PySpark or Ibis framework.  Why?  Well, why not?  Sometimes, it is good once in
a while, to step away from SQL world and venture into the world of dataframe-based APIs.  For most cases, you'll want to stick with SQL, but sometimes, it is convenient to use a
dataframe API.  One such convenience is to be able to write/save a dataframe directly to the database without having to execute DDL statements (CREATE TABLE) beforehand, especially if the
dataframe contains several columns.  Other conveniences such as being able to select columns by regex pattern or by data types, are also super nice since it would be difficult or
impossible to do using SQL.  It is because of these conveniences, I use dataframe API early on in a project or when doing a POC or ad-hoc analysis or doing something quick-n-dirty.
Then in later stages or when things need to be put into production, I converge to using SQL.  I think having both SQL and dataframe API knowledge is valuable for any data professional.

Why Ibis?  Well I want to learn or use something that is agnostic to an underlying backend technology.  PySpark fits the bill, but I don't particular like its dependency on the JVM.
What about pandas? Pandas is purely an in-memory dataframe API, so it isn't performant.  There's also Polars, but it can't handle big data, but handles up to "medium" data very well!
So I feel like Ibis is a good, balanced dataframe library that is likely to be "future-proof".  I could be wrong since currently, Ibis isn't widely used or popular.  I am still invested 
in learning PySpark only because that is where the job market is now and until the foreseeable future.  So that is why I choose to provide both PySpark and Ibis examples.  I believe as 
marketable skills, you can't go wrong with these 2 dataframe API frameworks.  Plus, when you know one dataframe API, it is very easy to pick up another.