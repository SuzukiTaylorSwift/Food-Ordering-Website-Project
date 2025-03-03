CREATE TABLE "auth_users" (
  "id" integer PRIMARY KEY,
  "email" varchar UNIQUE,
  "name" varchar,
  "password" varchar,
  "avatar_url" varchar,
  "role" varchar
);

CREATE TABLE "menus" (
  "id" integer PRIMARY KEY,
  "nameFood" varchar,
  "price" integer,
  "image_path" varchar,
  "type" varchar,
  "option" varchar
);

CREATE TABLE "tables" (
  "id" integer PRIMARY KEY,
  "status" varchar
);

CREATE TABLE "orders" (
  "id" integer PRIMARY KEY,
  "table_id" integer,
  "takeaway" boolean,
  "food_status" varchar,
  "paid_status" varchar,
  "totalPrice" integer,
  "order_time" timestamp,
  "is_deleted" boolean,
  "deleted_at" timestamp
);

CREATE TABLE "order_tables" (
  "id" integer PRIMARY KEY,
  "menu_id" integer,
  "order_id" integer,
  "totalPrice" integer,
  "quantity" integer,
  "option" varchar,
  "note" varchar,
  "is_deleted" boolean,
  "deleted_at" timestamp
);

ALTER TABLE "orders" ADD FOREIGN KEY ("table_id") REFERENCES "tables" ("id");

ALTER TABLE "order_tables" ADD FOREIGN KEY ("menu_id") REFERENCES "menus" ("id");

ALTER TABLE "order_tables" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");
