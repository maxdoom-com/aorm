all: test.db real-test

.PHONY: test.db

test.db: test.sql
	rm -f test.db
	sqlite3 $@ < $<

real-test:
	./test.py

