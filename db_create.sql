CREATE TABLE "tags" (
	"name"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	"user"	INTEGER NOT NULL,
	"cmd_id"	INTEGER NOT NULL,
	PRIMARY KEY("name")
)