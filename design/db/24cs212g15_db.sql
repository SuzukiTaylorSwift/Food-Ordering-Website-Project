CREATE TABLE "users" (
  "id" int PRIMARY KEY,
  "username" varchar,
  "password" varchar,
  "role" varchar,
  "avatar" varchar
);

CREATE TABLE "tables" (
  "id" int PRIMARY KEY,
  "status" varchar
);

CREATE TABLE "menu" (
  "id" int PRIMARY KEY,
  "name_food" varchar,
  "price" int,
  "image_path" varchar,
  "type" varchar,
  "option" varchar
);

CREATE TABLE "orders" (
  "id" int PRIMARY KEY,
  "table_id" int,
  "takeaway" boolean,
  "food_status" varchar,
  "paid_status" varchar,
  "order_time" datetime,
  "total_price" int
);

CREATE TABLE "order_list" (
  "id" int PRIMARY KEY,
  "order_id" int,
  "menu_id" int,
  "quantity" int,
  "total_price" int,
  "option" varchar
);

ALTER TABLE "orders" ADD FOREIGN KEY ("table_id") REFERENCES "tables" ("id");

ALTER TABLE "order_list" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");

ALTER TABLE "order_list" ADD FOREIGN KEY ("menu_id") REFERENCES "menu" ("id");
