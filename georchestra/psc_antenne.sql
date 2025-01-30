--
-- PostgreSQL database dump
--

-- Dumped from database version 13.5
-- Dumped by pg_dump version 13.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: psc; Type: SCHEMA; Schema: -; Owner: georchestra
--

CREATE SCHEMA psc;


ALTER SCHEMA psc OWNER TO georchestra;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: georchestra
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO georchestra;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: georchestra
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO georchestra;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: georchestra
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO georchestra;

--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: georchestra
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: antennes; Type: TABLE; Schema: psc; Owner: georchestra
--

CREATE TABLE psc.antennes (
    fid integer NOT NULL,
    the_geom public.geometry(Point,4326),
    gml_id character varying(254),
    id character varying(254),
    antennes character varying(254),
    adresse character varying(254),
    adr_num character varying(254),
    adr_suf character varying(254),
    adr_voie character varying(254),
    code_post character varying(254),
    com character varying(254),
    insee_com character varying(254),
    ant_tel character varying(254),
    ant_mail character varying(254),
    latitude character varying(254),
    longitude character varying(254),
    x_l93 character varying(254),
    y_l93 character varying(254),
    metadata character varying(254),
    inaugurati timestamp without time zone
);


ALTER TABLE psc.antennes OWNER TO georchestra;

--
-- Name: antennes_fid_seq; Type: SEQUENCE; Schema: psc; Owner: georchestra
--

CREATE SEQUENCE psc.antennes_fid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE psc.antennes_fid_seq OWNER TO georchestra;

--
-- Name: antennes_fid_seq; Type: SEQUENCE OWNED BY; Schema: psc; Owner: georchestra
--

ALTER SEQUENCE psc.antennes_fid_seq OWNED BY psc.antennes.fid;


--
-- Name: antennes fid; Type: DEFAULT; Schema: psc; Owner: georchestra
--

ALTER TABLE ONLY psc.antennes ALTER COLUMN fid SET DEFAULT nextval('psc.antennes_fid_seq'::regclass);


--
-- Data for Name: antennes; Type: TABLE DATA; Schema: psc; Owner: georchestra
--

COPY psc.antennes (fid, the_geom, gml_id, id, antennes, adresse, adr_num, adr_suf, adr_voie, code_post, com, insee_com, ant_tel, ant_mail, latitude, longitude, x_l93, y_l93, metadata, inaugurati) FROM stdin;
1	0101000020E610000054EB58D867E025418C7F619B87BC5A41	antennes.ar_02	ar_02	CAMBRAI	5 rue d'Alger	5		r d'Alger	59400	Cambrai	59122	0374278003	Antennes-Cambrai@hautsdefrance.fr	50,1770908006218	3,23564890297393	716851,9225534	7008798,42782582	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2018-12-11 00:00:00
2	0101000020E61000001EB2D48E251024419DC0916C76665A41	antennes.ar_04	ar_04	CLERMONT	4 avenue des DÃ©portÃ©s	4		av des DÃ©portÃ©s	60600	Clermont	60157	0374273040	Antennes-Clermont@hautsdefrance.fr	49,384075	2,413835	657426,778966494	6920665,69639602	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2017-01-23 00:00:00
3	0101000020E61000005792E1BF62452641911E127A95405A41	antennes.ar_03	ar_03	CHATEAU-THIERRY	2 avenue Ernest Couvrecelle	2		av Ernest Couvrecelle	02400	Etampes-sur-Marne	02292	0374278133	antennes-chateau-thierry@hautsdefrance.fr	49,0360971240337	3,40723630201098	729777,374799997	6881877,9074	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2019-09-13 00:00:00
4	0101000020E6100000A1A5C817FCA3274166D5ABE36AAB5A41	antennes.ar_05	ar_05	FOURMIES	1 place Georges Coppeaux	1		pl Georges Coppeaux	59610	Fourmies	59249	0374273020	antennes-fourmies@hautsdefrance.fr	50,0155263825089	4,04063846400173	774654,046452685	6991275,55736289	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2016-11-28 00:00:00
5	0101000020E6100000B306730AD0D22341DC6713A3B8C75A41	antennes.ar_06	ar_06	FREVENT	2 rue des Lombards	2		r des Lombards	62270	FrÃ©vent	62361	0374273070	Antennes-Frevent@hautsdefrance.fr	50,278196	2,293479	649576,020408826	7020258,54805943	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2018-05-22 00:00:00
6	0101000020E6100000FE9BF6A04165244167ABBB095EF75A41	antennes.ar_07	ar_07	HAZEBROUCK	222 bis rue de vieux Berquin	222	bis	r de vieux Berquin	59190	Hazebrouck	59295	0374278123	antennes-hazebrouck@hautsdefrance.fr	50,717351	2,55224	668320,814381481	7069048,15207944	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2019-05-21 00:00:00
7	0101000020E6100000B96697C44DD12341F32DBFC4689D5A41	antennes.ar_01	ar_01	AMIENS	15 mail Albert 1er	15		mail Albert 1er	80000	Amiens	80021	0374273003	antennes-amiens@hautsdefrance.fr	49,889068	2,296184	649382,883967602	6976931,07416867	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2018-05-22 00:00:00
8	0101000020E6100000F440F95FD5662441A8E0B4706B825A41	antennes.ar_08	ar_08	MONTDIDIER	41 rue Jean Jaures	41		r Jean Jaures	80500	Montdidier	80561	0374273010	antennes-montdidier@hautsdefrance.fr	49,642003	2,56443	668522,687448531	6949293,76103989	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2018-04-25 00:00:00
9	0101000020E6100000686CB76C3EDE2441DD63E50A9AC95A41	antennes.ar_12	ar_12	ARRAS	13 ter boulevard Robert Schuman	13	ter	boulevard Robert Schuman	62000	Arras	62041	0374278151	antennes-arras@hautsdefrance.fr	50,2973020552503	2,7730300312276	683807,212300003	7022184,1703	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	\N
10	0101000020E61000004BDE085C2103234175ED030DDB845A41	antennes.ar_13	ar_13	GRANDVILLIERS	CitÃ© des mÃ©tiers, 11 avenue Saget	11		av Saget	60210	Grandvilliers	60286	0374278170	antennes-Grandivilliers@hautsdefrance.fr	49,6605268787437	1,93399257050175	622992,679799996	6951788,2034	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	\N
11	0101000020E610000090D8CD5897B02241B5A0FF9BDADC5A41	antennes.ar_09	ar_09	MONTREUIL-SUR-MER	5 rue Saint-Gengoult	5		r Saint-Gengoult	62170	Montreuil-sur-Mer	62588	0374278111	antennes-montreuil-sur-mer@hautsdefrance.fr	50,468364	1,768308	612427,673445477	7041898,43747728	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2019-06-24 00:00:00
12	0101000020E61000004E5D1A997A12264184B6200A7C655A41	antennes.ar_11	ar_11	SOISSONS	2 allÃ©e des Nobel	2		all des Nobel	02200	Soissons	02722	0374273034	antennes-soissons@hautsdefrance.fr	49,376069	3,320219	723261,299029266	6919664,15824664	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2016-12-12 00:00:00
13	0101000020E6100000D0EBD3EEECD422419578A9782FB55A41	antennes.ar_14	ar_14	ABBEVILLE	1 rue Paul Delique (au sein du lycÃ©e Boucher de Perthes)	1		r Paul Delique	80100	Abbeville	80001	0374278090	antennes-abbeville@hautsdefrance.fr	50,104318770141	1,84208832322462	617078,466499999	7001277,8853	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	\N
14	0101000020E61000004022F954DBFC2541D0D9DF2B15985A41	antennes.ar_10	ar_10	SAINT-QUENTIN	58 boulevard Victor Hugo	58		boulevard Victor Hugo	02100	Saint-Quentin	02691	0374278010	antennes-saintquentin@hautsdefrance.fr	49,8417627292716	3,28469121785817	720493.6659632446	6971476.68553777	https://geocatalogue.hautsdefrance.fr/geonetwork/srv/fre/catalog.search#/metadata/4b5f8e1b-de37-47cd-9203-37a59f318b09	2023-01-06 00:00:00
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: georchestra
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: georchestra
--

COPY tiger.geocode_settings (name, setting, unit, category, short_desc) FROM stdin;
\.


--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: georchestra
--

COPY tiger.pagc_gaz (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: georchestra
--

COPY tiger.pagc_lex (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: georchestra
--

COPY tiger.pagc_rules (id, rule, is_custom) FROM stdin;
\.


--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: georchestra
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
\.


--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: georchestra
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- Name: antennes_fid_seq; Type: SEQUENCE SET; Schema: psc; Owner: georchestra
--

SELECT pg_catalog.setval('psc.antennes_fid_seq', 14, true);


--
-- Name: antennes antennes_pkey; Type: CONSTRAINT; Schema: psc; Owner: georchestra
--

ALTER TABLE ONLY psc.antennes
    ADD CONSTRAINT antennes_pkey PRIMARY KEY (fid);


--
-- Name: spatial_antennes_the_geom; Type: INDEX; Schema: psc; Owner: georchestra
--

CREATE INDEX spatial_antennes_the_geom ON psc.antennes USING gist (the_geom);


--
-- PostgreSQL database dump complete
--

