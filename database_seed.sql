-- Seed data for RegistraMe (PostgreSQL compatible, idempotent)
-- Run AFTER migrations: docker compose exec backend python manage.py migrate
-- Usage: docker exec -i registrame-db psql -U postgres -d registrame_db < database_seed.sql

BEGIN;

-- Categories
INSERT INTO "categories_productcategory" ("catproCod","catproCode","catproNom","catproRequiereInventario") VALUES
(1,'AC','Accesorios',TRUE),
(2,'MO','Monturas',TRUE),
(3,'LUNA','Lunas',FALSE)
ON CONFLICT ("catproCod") DO NOTHING;

-- Suppliers
INSERT INTO "suppliers_supplier" ("provCod","provRuc","provRazSocial","provDirec","provEmail","provCiu","provEstado","provTele") VALUES
(1,'00000000000','Proveedor Genérico','No especificado','generico@proveedor.com','N/A','Active','999999999')
ON CONFLICT ("provCod") DO NOTHING;

-- Roles
INSERT INTO "users_role" ("rolCod","rolNom","rolDes","rolEstado","rolNivel") VALUES
(1,'GERENTE','Gerente','ACTIVO',0),
(2,'CAJERO','Cajero','ACTIVO',2),
(3,'VENDEDOR','Vendedor','ACTIVO',2),
(4,'OPTOMETRA','Optometra','ACTIVO',4),
(5,'LOGISTICA','Logística','ACTIVO',3)
ON CONFLICT ("rolCod") DO NOTHING;

-- Users (password: Admin123!)
INSERT INTO "users_user" ("last_login","is_superuser","usuCod","usuNom","password","usuNombreCom","usuDNI","usuTel","usuEmail","usuEstado","is_staff","is_active","date_joined") VALUES
(NULL,TRUE,1,'gerente1','pbkdf2_sha256$1000000$w8qGOvFQCBfDxZxikHnK3A$6ZlS4ZC6yuD+ynvYy2t101fUxLtc5VvM50dRVuPNHyY=','Gerente de Prueba','99999999','999999998','gerente1@registrame.com',TRUE,TRUE,TRUE,'2026-06-09 12:48:23.000000+00'),
(NULL,FALSE,2,'cajero1','pbkdf2_sha256$1000000$n3Uim64wOxGU8OnnvqNwY0$tQZO1/Opsdk+rvs1ugKBEVdTObSnFPLh1GFR2UpTa+s=','Cajero de Prueba','88888888','888888888','cajero1@registrame.com',TRUE,FALSE,TRUE,'2026-06-09 12:48:24.214390+00'),
(NULL,FALSE,3,'vendedor1','pbkdf2_sha256$1000000$YY10wSMkThthFeOwuleeZt$yVSc9CH1Ngqn6m1XlFuKJ7YVfr34F+h9D0DAGaggLuc=','Vendedor de Prueba','77777777','777777777','vendedor1@registrame.com',TRUE,FALSE,TRUE,'2026-06-09 12:48:25.002607+00'),
(NULL,FALSE,4,'optometra1','pbkdf2_sha256$1000000$UB9WpmaF1TZbJLCRuOBqal$SWyA7RYoopIWhqPUeojs1tP0OPWg12SSBEd/FKCaf78=','Optometra de Prueba','66666666','666666666','optometra1@registrame.com',TRUE,FALSE,TRUE,'2026-06-09 12:48:26.000000+00'),
(NULL,FALSE,5,'logistica1','pbkdf2_sha256$1000000$1Fj54nOfuOuzfieXveacN1$EW1lshnk3xQLX6b3OrkaGfozKrqE96Js6tIIbUE4rAY=','Logistica de Prueba','55555555','555555555','logistica1@registrame.com',TRUE,FALSE,TRUE,'2026-06-09 12:48:27.000000+00')
ON CONFLICT ("usuCod") DO NOTHING;

-- User-Role assignments
INSERT INTO "users_user_roles" ("id","user_id","role_id") VALUES
(1,1,1),
(2,2,2),
(3,3,3),
(4,4,4),
(5,5,5)
ON CONFLICT ("id") DO NOTHING;

-- Cashes
INSERT INTO "cash" ("cajCod","usuCod_id","cajNom","cajDes","cajEstado","created_at","updated_at") VALUES
(1,1,'Caja Principal (Gerente)','Caja de administración','ACTIVO','2026-06-09 12:48:00.000000+00','2026-06-09 12:48:00.000000+00'),
(2,2,'Caja 1 (Cajero)','Caja de facturación 1','ACTIVO','2026-06-09 12:48:00.000000+00','2026-06-09 12:48:00.000000+00'),
(3,3,'Caja 2 (Vendedor)','Caja de ventas directas','ACTIVO','2026-06-09 12:48:00.000000+00','2026-06-09 12:48:00.000000+00')
ON CONFLICT ("cajCod") DO NOTHING;

-- Products
INSERT INTO "product" ("prodCod","prodCode","prodDescr","prodMarca","prodMate","prodColor","prodTalla","prodGenero","prodCostoInv","prodPrecioVenta","prodStock","prodStockMin","prodEstado","created_at","updated_at","catproCod_id","provCod_id","prodDescripcionAdicional","prodForma","prodTieneSobrelente") VALUES
(1,'LUNA-PERS','LUNA PERSONALIZADA','PERSONALIZADO','N','','','Unisex',0,0,9999,0,'Active','2026-06-09 12:46:47.511963+00','2026-06-09 12:46:47.511963+00',3,1,'Producto genérico para lunas con configuración personalizada. NO consume stock.','',FALSE),
(2,'M1','PEGASUS | 52-19 DORADA - PG M3047','PEGASUS','M','DORADA','52-19','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.079005+00','2026-06-09 12:48:15.079005+00',2,1,'PG M3047','',FALSE),
(3,'M2','PEGASUS | 56-18 DORADA AVIADOR - PG M3052 Doble Puente','PEGASUS','M','DORADA','56-18','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.093604+00','2026-06-09 12:48:15.093604+00',2,1,'PG M3052 Doble Puente','AVIADOR',FALSE),
(4,'M3','VIPSUAL | 53-18-145 DORADO - VM2508','VIPSUAL','M','DORADO','53-18-145','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.106824+00','2026-06-09 12:48:15.106824+00',2,1,'VM2508','',FALSE),
(5,'M4','VIPSUAL | 55-18-145 DORADO - VM2509','VIPSUAL','M','DORADO','55-18-145','Unisex',0,0,2,0,'Active','2026-06-09 12:48:15.122271+00','2026-06-09 12:48:15.122271+00',2,1,'VM2509','',FALSE),
(6,'M5','CARLOS ROSSI | 53-18-145 NEGRO PLATEADO - 73088','CARLOS ROSSI','M','NEGRO PLATEADO','53-18-145','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.135563+00','2026-06-09 12:48:15.135563+00',2,1,'73088','',FALSE),
(7,'M6','CARLOS ROSSI | 51-18-143 PLATEADO HEXAGONAL - 73083','CARLOS ROSSI','M','PLATEADO','51-18-143','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.151825+00','2026-06-09 12:48:15.151825+00',2,1,'73083','HEXAGONAL',FALSE),
(8,'M7','CARLOS ROSSI | 51-18-143 PLATEADO DORADO HEXAGONAL - 73083','CARLOS ROSSI','M','PLATEADO DORADO','51-18-143','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.166753+00','2026-06-09 12:48:15.166753+00',2,1,'73083','HEXAGONAL',FALSE),
(9,'M8','CARLOS ROSSI | 51-18-143 NEGRO PLATEADO HEXAGONAL - 73083','CARLOS ROSSI','M','NEGRO PLATEADO','51-18-143','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.180957+00','2026-06-09 12:48:15.180957+00',2,1,'73083','HEXAGONAL',FALSE),
(10,'M9','CARLOS ROSSI | 51-18-143 NEGRO DORADO HEXAGONAL - 73083','CARLOS ROSSI','M','NEGRO DORADO','51-18-143','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.195322+00','2026-06-09 12:48:15.195322+00',2,1,'73083','HEXAGONAL',FALSE),
(11,'M10','CARLOS ROSSI | 51-18-143 NEGRO HEXAGONAL - 73083','CARLOS ROSSI','M','NEGRO','51-18-143','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.207422+00','2026-06-09 12:48:15.207422+00',2,1,'73083','HEXAGONAL',FALSE),
(12,'M11','TENDENCIA | 54-17-142 DORADO NUDE - C5 Biselado al aire','TENDENCIA','M','DORADO NUDE','54-17-142','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.221933+00','2026-06-09 12:48:15.221933+00',2,1,'C5 Biselado al aire','',FALSE),
(13,'M12','OZZY | 55-16-140 NEGRO BLANCO DORADO POLIGONAL - HZ8001 C5','OZZY','M','NEGRO BLANCO DORADO','55-16-140','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.236412+00','2026-06-09 12:48:15.236412+00',2,1,'HZ8001 C5','POLIGONAL',FALSE),
(14,'M13','OZZY | 52-18-140 NEGRO ROSA PLATEADO - HZ8003 C4','OZZY','M','NEGRO ROSA PLATEADO','52-18-140','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.250292+00','2026-06-09 12:48:15.250292+00',2,1,'HZ8003 C4','',FALSE),
(15,'M14','FEILLIS | 56-15-144 NEGRO AVIADOR [Con Sobrelente] - 8015 Doble Puente - 4 Sobrelentes','FEILLIS','M','NEGRO','56-15-144','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.263647+00','2026-06-09 12:48:15.263647+00',2,1,'8015 Doble Puente - 4 Sobrelentes','AVIADOR',TRUE),
(16,'1','LUNA PERSONALIZADA','','N','','','Unisex',0,0,1,0,'Active','2026-06-09 12:48:15.275270+00','2026-06-09 12:48:15.275270+00',1,1,'LUNA PERSONALIZADA','',FALSE)
ON CONFLICT ("prodCod") DO NOTHING;

-- Product sequences
INSERT INTO "product_sequence" ("id","sequence_type","current_value","description","created_at","updated_at") VALUES
(1,'A',0,'Monturas de Acetato','2026-06-09 12:46:47.892902+00','2026-06-09 12:46:47.892902+00'),
(2,'M',14,'Monturas de Metal','2026-06-09 12:46:47.894895+00','2026-06-09 12:46:47.894895+00'),
(3,'TR',0,'Monturas TR','2026-06-09 12:46:47.896899+00','2026-06-09 12:46:47.896899+00'),
(4,'C',0,'Monturas de Carey','2026-06-09 12:46:47.897896+00','2026-06-09 12:46:47.897896+00'),
(5,'GENERAL',1,'Productos no monturas','2026-06-09 12:46:47.900273+00','2026-06-09 12:46:47.900273+00')
ON CONFLICT ("id") DO NOTHING;

-- Luna materials
INSERT INTO "luna_material" ("lunMatCod","lunMatNombre","lunMatDescripcion","lunMatActivo") VALUES
(1,'NK','Material NK',TRUE),
(2,'Policarbonato','Material ligero y resistente',TRUE),
(3,'Resina','Material de resina',TRUE),
(4,'Cristal','Material tradicional de alta calidad',TRUE),
(5,'Otros','Otros materiales',TRUE)
ON CONFLICT ("lunMatCod") DO NOTHING;

-- Luna types
INSERT INTO "luna_tipo" ("lunTipCod","lunTipNombre","lunTipDescripcion","lunTipActivo") VALUES
(1,'Monofocal','Corrección para una distancia',TRUE),
(2,'Bifocal','Corrección para dos distancias',TRUE),
(3,'Multifocal','Corrección para múltiples distancias',TRUE)
ON CONFLICT ("lunTipCod") DO NOTHING;

-- Luna characteristics
INSERT INTO "luna_caracteristica" ("lunCarCod","lunCarNombre","lunCarDescripcion","lunCarPrecioAdicional","lunCarActivo") VALUES
(1,'Blue Block','Filtro luz azul',30,TRUE),
(2,'UV400','Protección UV completa',20,TRUE),
(3,'AR','Anti-reflejo',40,TRUE),
(4,'Fotocromatico','Se oscurece con luz solar',80,TRUE),
(5,'Polarizado','Elimina deslumbramiento',60,TRUE),
(6,'Alto Indice','Lentes más delgados',50,TRUE),
(7,'Digital','Protección luz digital',45,TRUE),
(8,'Coloreado','Luna con color personalizado',35,TRUE)
ON CONFLICT ("lunCarCod") DO NOTHING;

-- Luna configurations (material x tipo price matrix)
INSERT INTO "luna_configuracion" ("lunConfCod","lunConfPrecioBase","lunConfActivo","lunMatCod_id","lunTipCod_id") VALUES
(1,100,TRUE,1,1),
(2,180,TRUE,1,2),
(3,280,TRUE,1,3),
(4,120,TRUE,2,1),
(5,200,TRUE,2,2),
(6,300,TRUE,2,3),
(7,90,TRUE,3,1),
(8,160,TRUE,3,2),
(9,250,TRUE,3,3),
(10,110,TRUE,4,1),
(11,190,TRUE,4,2),
(12,290,TRUE,4,3),
(13,80,TRUE,5,1),
(14,150,TRUE,5,2),
(15,240,TRUE,5,3)
ON CONFLICT ("lunConfCod") DO NOTHING;

COMMIT;
