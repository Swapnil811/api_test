The book list API is on endpoint /books (GET METHOD)

INPUT

Pagination control
    1) page => page number, defaults to 1
    2) per_page => number of results per page, defaults to 25
    3) sort_by => column name in books_book, defaults to download_count
    4) sort => direction either asc or desc , defaults to desc
    5) operator => filter condition either "and" or "or" , defaults to or

available filters

    for all filters below you can pass multiple filter critera by comma delimited string
    e.g to filter on language either for en or fr call "/books?language=en,fr"

    1) book_id => filters on gutenberg_id in books_book table
    2) language => language code to filter
    3) mime_type => mime_type
    4) topic => partial subject or bookshelf case insensitive
    5) author => partial author name case insensitive
    6) title => partial book title case insensitive



OUTPUT
    outputs json {"total": <int>, "books": <list of book objects>}