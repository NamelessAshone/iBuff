drop table if exists workouts;
drop table if exists exercises;
drop table if exists weights;

CREATE TABLE `workouts` (
  `id`	integer PRIMARY KEY AUTOINCREMENT,
  `title`	text NOT NULL,
  `comment`	text NOT NULL
);

CREATE TABLE `exercises` (
  `id`	integer PRIMARY KEY AUTOINCREMENT,
  `workout_id`	integer NOT NULL,
  `title`	text NOT NULL,
  `comment`	text NOT NULL,
  `sets`	integer NOT NULL,
  `reps`	integer NOT NULL
);

CREATE TABLE `history` (
  `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
  `exercise_id`	INTEGER NOT NULL,
  `workout_id`	INTEGER NOT NULL,
  `sets`	INTEGER NOT NULL,
  `reps`	INTEGER NOT NULL,
  `weight`	INTEGER NOT NULL,
  `date_time`	TEXT NOT NULL
);