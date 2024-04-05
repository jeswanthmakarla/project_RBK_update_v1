BEGIN TRANSACTION;
CREATE TABLE crops_queue (
    crop_id INTEGER PRIMARY KEY,
    rbk_id INTEGER,
    farmer_name TEXT,
    mandal TEXT,
    survey_no TEXT,
    crop_type TEXT,
    cut_date TEXT,
    qc_date TEXT,
    qc_check TEXT,
    sell_date TEXT,
    bags_req TEXT,
    vehicle_type_req TEXT,
    pick_up_time TEXT,
    pick_up_address TEXT,
    amount INTEGER,
    status TEXT);
INSERT INTO "crops_queue" VALUES(9898,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "crops_queue" VALUES(9899,1001,'Poorna V S L','Bandar','987','Paddy','21-01-2023','25-02-2023','False','10-02-2023','50','Tractor','16:30','1-121, Chilakalapudi, Machilipatnam',NULL,'Processing');
CREATE TABLE farmers (
    id INTEGER PRIMARY KEY,
    rbk_id INTEGER,
    fullname TEXT,
    phone TEXT,
    bank_ac TEXT,
    aadhaar_no TEXT,
    address TEXT,
    mandal TEXT,
    village TEXT);
INSERT INTO "farmers" VALUES(1,1001,'Poorna V S L','9876543210','0009876543211','123456789098','1-121, Chilakalapudi, Machilipatnam','Bandar','Chilakalapudi');
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    assigned_rbk INTEGER,
    c_fullname TEXT,
    c_phone TEXT,
    survey_no INTEGER,
    message TEXT,
    status TEXT);
INSERT INTO "messages" VALUES(1,1001,'Poorna V S L','9876543210',987,'Hi,

i''ve sent the crop details.
please validate and assign me transport and rice mill

Thank you RBK','in-progress');
INSERT INTO "messages" VALUES(2,1001,'Tharun Narasimha M','9988776655','undefined','hi.. 

i''ve updated my available dates.

please assign me some transports work.

Thank you RBK','in-progress');
INSERT INTO "messages" VALUES(3,1001,'Jeswanth','9998887776','undefined','hi,

i''m up to date on my rice mill info.

assign me some miling work from farmers.','in-progress');
CREATE TABLE ricemill_owners (
    id INTEGER PRIMARY KEY,
    rbk_id INTEGER,
    fullname TEXT,
    millname TEXT,
    mill_phone TEXT,
    address TEXT,
    mandal TEXT,
    village TEXT,
    storage_capacity INTEGER,
    milling_capacity INTEGER,
    dispatched_bags INTEGER);
INSERT INTO "ricemill_owners" VALUES(1,1001,'Jeswanth','Sri Venkateswara Ricemill','9998887776','12-32/212, Ramanaidupeta, Machilipatnam','Bandar','Ramanaidupeta',450,250,0);
CREATE TABLE ricemill_queue (
    id INTEGER PRIMARY KEY,
    millname TEXT,
    mill_phone TEXT,

    crop_id INTEGER,
    survey_no INTEGER,
    crop_get_date TEXT,
    c_fullname TEXT,
    c_phone TEXT,
    no_of_bags INTEGER,
    bags_status TEXT,

    track_id INTEGER,
    t_fullname TEXT,
    t_phone TEXT,
    vehicle_type TEXT,
    vehicle_no TEXT);
CREATE TABLE surveys (
    id INTEGER PRIMARY KEY,
    phone TEXT,
    survey_no TEXT,
    land_capacity TEXT,
    land_passbook TEXT);
INSERT INTO "surveys" VALUES(1,'9876543210','987','50','0987654321');
CREATE TABLE transport_owners (
    id INTEGER PRIMARY KEY,
    rbk_id INTEGER,
    fullname TEXT,
    phone TEXT,
    address TEXT,
    mandal TEXT,
    village TEXT,
    trips TEXT,
    vehicle_type TEXT,
    vehicle_no TEXT,
    vehicle_rec TEXT,
    available_dates TEXT);
INSERT INTO "transport_owners" VALUES(1,1001,'Tharun Narasimha M','9988776655','453-45/3, Parasupeta, Machilipatnam','Bandar','Parasupeta','0/0' ,'Tractor','AP 16 AZ 4321','Documents Provided','["2023-03-09","2023-03-10","2023-03-11"]');
CREATE TABLE transport_queue (
    track_id INTEGER PRIMARY KEY,
    crop_id INTEGER,
    c_fullname TEXT,
    c_phone TEXT,
    d_fullname TEXT,
    d_phone TEXT,
    date_booked TEXT,
    time_slot TEXT,
    from_ TEXT,
    to_ TEXT,
    vehicle_type TEXT,
    vehicle_no TEXT,
    status TEXT);
INSERT INTO "transport_queue" VALUES(300101,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    phone TEXT,
    password TEXT,
    user_type TEXT);
INSERT INTO "users" VALUES(1,'9876543210','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','farmer');
INSERT INTO "users" VALUES(2,'9988776655','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','transport');
INSERT INTO "users" VALUES(3,'9998887776','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','ricemill');

CREATE TABLE rbk_users (
    rbk_id INTEGER PRIMARY KEY,
    fullname TEXT,
    phone TEXT,
    password TEXT,
    mandal TEXT,
    village TEXT);
INSERT INTO "rbk_users" VALUES(1001,'RBK Bandar', '9999988888', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Bandar', 'Chilakalapudi');
CREATE TABLE places (
    id INTEGER PRIMARY KEY,
    mandal TEXT,
    village TEXT);
INSERT INTO "places" VALUES(1,'Bandar', 'Chilakalapudi');
INSERT INTO "places" VALUES(2,'Bandar', 'Parasupeta');
INSERT INTO "places" VALUES(3,'Bandar', 'Ramanaidupeta');
INSERT INTO "places" VALUES(4,'Pedana', 'Balliparru');
INSERT INTO "places" VALUES(5,'Pedana', 'Chennuru');
COMMIT;
