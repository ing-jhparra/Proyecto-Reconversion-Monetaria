CREATE OR REPLACE function sp_sanosDiccionarios (valor INT)
returns void
language plpgsql AS 
$$
DECLARE registros INT = 0;	
        entidad VARCHAR(100) := NULL;
        comando VARCHAR(1000) := NULL;
        tupla  RECORD;
        columna RECORD;
DECLARE tabla  CURSOR FOR
            SELECT table_schema,table_name 
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog','information_schema') and table_type = 'BASE TABLE' 
                              AND table_name NOT IN ('inventario_articulo_ambulatorio', 'aps_cliente_especialidad')
            ORDER BY table_schema,table_name;
BEGIN
    DROP TABLE IF EXISTS sanos_diccionario;
    CREATE TABLE sanos_diccionario (esquema varchar(50), nombretabla varchar(50),nombrecampo varchar(50));
    FOR tupla IN tabla LOOP
       entidad = tupla.table_schema ||'.'||tupla.table_name;
       EXECUTE format('SELECT COUNT (*) FROM %s', entidad) INTO registros;
       IF registros > 0 THEN
		DECLARE campos CURSOR FOR SELECT i.table_schema as esquema, i.table_name as nombre_t, i.column_name as nombre_c
                                         FROM   information_schema.columns i
                                         where i.data_type='numeric'
                                         AND i.column_name NOT in ('factor_erp','conteo','equivalencia','ajuste','factor','p_iva','p_descuento')
                                         AND i.column_name NOT ILIKE '%cantidad%'
                                         AND i.column_name NOT ILIKE '%existencia%'
                                         AND i.column_name NOT ILIKE '%porcentaje%'
                                         AND i.column_name NOT ILIKE '%peso%'
                                         AND i.column_name NOT ILIKE '%porc%'
                                         AND i.column_name NOT ILIKE '%consumido%'
                                         AND i.column_name NOT ILIKE '%dosis%'
                                         AND i.column_name NOT ILIKE '%cant%'
                                         AND i.column_name NOT ILIKE '%valor%'
                                         AND i.table_name = tupla.table_name;
                BEGIN
                   for  columna in campos LOOP
                        insert into sanos_diccionario(esquema,nombretabla,nombrecampo) VALUES (columna.esquema,columna.nombre_t,columna.nombre_c);
                   END LOOP;                   
                END;
       END IF;
    END LOOP;
END;
$$;

SELECT sp_sanosDiccionarios (1);

select * from sanos_diccionario;

DO $$
DECLARE usuarios VARCHAR(100)[] := array ['reconversion_user'];
DECLARE usuario VARCHAR(100) := NULL;
DECLARE entidad_esquema VARCHAR(100) := NULL;
DECLARE nombre_esquema  RECORD;
DECLARE esquema  CURSOR FOR SELECT DISTINCT table_schema
 FROM information_schema.tables
 WHERE table_schema NOT IN ('pg_catalog','information_schema') and table_type = 'BASE TABLE';
BEGIN
  FOR login IN array_lower(usuarios, 1)..array_upper(usuarios, 1) LOOP
    usuario := usuarios[login];
    FOR nombre_esquema IN esquema LOOP
EXECUTE format('GRANT USAGE  ON SCHEMA %s  TO %s;', nombre_esquema.table_schema,usuario);
EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA  %s  TO %s;', nombre_esquema.table_schema,usuario);
EXECUTE format('GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA %s TO %s;', nombre_esquema.table_schema,usuario);
EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA %s TO %s;', nombre_esquema.table_schema,usuario);
    END LOOP;
  END LOOP;
END;
$$

ALTER TABLE presupuesto.baremo_detalle DISABLE TRIGGER trg_biu_baremo_detalle_hm;
ALTER TABLE inventario_detalle_movimiento DISABLE TRIGGER trg_bidu_invdetmovimiento;



ALTER TABLE presupuesto.baremo_detalle ENABLE TRIGGER trg_biu_baremo_detalle_hm;
ALTER TABLE inventario_detalle_movimiento DISABLE TRIGGER trg_bidu_invdetmovimiento;

select event_object_schema as table_schema,
       event_object_table as table_name,
       trigger_schema,
       trigger_name,
       string_agg(event_manipulation, ',') as event,
       action_timing as activation,
       action_condition as condition,
       action_statement as definition
from information_schema.triggers
group by 1,2,3,4,6,7,8
order by table_schema,
         table_name;

select  max(costo_promedio), max(costo_unitario_presentacion), max(costo_venta), max(monto_hm), max(precio_venta_unitario), max(ultimo_costo) 
from public.inventario_detalle_movimiento
select m(monto_hm) from presupuesto.baremo_detalle

select * from sanos_diccionario where nombrecampo ilike '%monto_hm%'
min(monto_comision), min(monto_hm

UPDATE public.inventario_detalle_movimiento SET costo_promedio = ROUND(costo_promedio/1000000,4), costo_unitario_presentacion = ROUND(costo_unitario_presentacion/1000000,4), costo_venta = ROUND(costo_venta/1000000,4), monto_hm = ROUND(monto_hm/1000000,4), precio_venta_unitario = ROUND(precio_venta_unitario/1000000,4), ultimo_costo = ROUND(ultimo_costo/1000000,4);

--------------------------------------------------------------------------
SELECT pg_terminate_backend(pg_stat_activity.pid) 
FROM pg_stat_activity 
WHERE pg_stat_activity.datname = 'sanos_test' 
AND pid <> pg_backend_pid();

drop database sanos_test;

CREATE DATABASE sanos_test WITH TEMPLATE temp_sanos_test OWNER postgres;

----------------------------------------------------------------------------------



