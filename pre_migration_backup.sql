--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13
-- Dumped by pg_dump version 14.15 (Homebrew)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: addresses; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.addresses (
    id integer NOT NULL,
    property_id uuid NOT NULL,
    house_number character varying NOT NULL,
    street character varying NOT NULL,
    city character varying NOT NULL,
    postcode character varying NOT NULL,
    latitude double precision,
    longitude double precision
);


ALTER TABLE public.addresses OWNER TO maisondbadmin;

--
-- Name: addresses_id_seq; Type: SEQUENCE; Schema: public; Owner: maisondbadmin
--

CREATE SEQUENCE public.addresses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.addresses_id_seq OWNER TO maisondbadmin;

--
-- Name: addresses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maisondbadmin
--

ALTER SEQUENCE public.addresses_id_seq OWNED BY public.addresses.id;


--
-- Name: offer_transactions; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.offer_transactions (
    id uuid NOT NULL,
    negotiation_id uuid NOT NULL,
    offer_amount integer NOT NULL,
    made_by character varying(128) NOT NULL,
    created_at timestamp with time zone
);


ALTER TABLE public.offer_transactions OWNER TO maisondbadmin;

--
-- Name: properties; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.properties (
    id uuid NOT NULL,
    price integer NOT NULL,
    bedrooms integer,
    bathrooms double precision,
    main_image_url character varying(500),
    seller_id character varying(128) NOT NULL,
    created_at timestamp with time zone,
    last_updated timestamp with time zone,
    status character varying(20) NOT NULL,
    CONSTRAINT valid_property_status CHECK (((status)::text = ANY ((ARRAY['for_sale'::character varying, 'under_offer'::character varying, 'sold'::character varying])::text[])))
);


ALTER TABLE public.properties OWNER TO maisondbadmin;

--
-- Name: property_details; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.property_details (
    id integer NOT NULL,
    property_id uuid NOT NULL,
    description character varying,
    construction_year integer,
    heating_type character varying
);


ALTER TABLE public.property_details OWNER TO maisondbadmin;

--
-- Name: property_details_id_seq; Type: SEQUENCE; Schema: public; Owner: maisondbadmin
--

CREATE SEQUENCE public.property_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.property_details_id_seq OWNER TO maisondbadmin;

--
-- Name: property_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maisondbadmin
--

ALTER SEQUENCE public.property_details_id_seq OWNED BY public.property_details.id;


--
-- Name: property_features; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.property_features (
    id integer NOT NULL,
    property_id uuid NOT NULL,
    has_garden boolean,
    garden_size double precision,
    parking_spaces integer,
    has_garage boolean
);


ALTER TABLE public.property_features OWNER TO maisondbadmin;

--
-- Name: property_features_id_seq; Type: SEQUENCE; Schema: public; Owner: maisondbadmin
--

CREATE SEQUENCE public.property_features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.property_features_id_seq OWNER TO maisondbadmin;

--
-- Name: property_features_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maisondbadmin
--

ALTER SEQUENCE public.property_features_id_seq OWNED BY public.property_features.id;


--
-- Name: property_media; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.property_media (
    id integer NOT NULL,
    property_id uuid NOT NULL,
    image_url character varying NOT NULL,
    image_type character varying NOT NULL,
    display_order integer
);


ALTER TABLE public.property_media OWNER TO maisondbadmin;

--
-- Name: property_media_id_seq; Type: SEQUENCE; Schema: public; Owner: maisondbadmin
--

CREATE SEQUENCE public.property_media_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.property_media_id_seq OWNER TO maisondbadmin;

--
-- Name: property_media_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maisondbadmin
--

ALTER SEQUENCE public.property_media_id_seq OWNED BY public.property_media.id;


--
-- Name: property_negotiations; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.property_negotiations (
    id uuid NOT NULL,
    property_id uuid,
    buyer_id character varying(128),
    status character varying(20) NOT NULL,
    last_offer_by character varying(128),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    accepted_by character varying(128),
    accepted_at timestamp with time zone,
    rejected_by character varying(128),
    rejected_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    CONSTRAINT valid_negotiation_status CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'accepted'::character varying, 'rejected'::character varying, 'cancelled'::character varying, 'withdrawn'::character varying, 'expired'::character varying])::text[])))
);


ALTER TABLE public.property_negotiations OWNER TO maisondbadmin;

--
-- Name: property_specs; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.property_specs (
    id integer NOT NULL,
    property_id uuid NOT NULL,
    bedrooms integer NOT NULL,
    bathrooms integer NOT NULL,
    reception_rooms integer NOT NULL,
    square_footage double precision NOT NULL,
    property_type character varying NOT NULL,
    epc_rating character varying NOT NULL
);


ALTER TABLE public.property_specs OWNER TO maisondbadmin;

--
-- Name: property_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: maisondbadmin
--

CREATE SEQUENCE public.property_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.property_specs_id_seq OWNER TO maisondbadmin;

--
-- Name: property_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maisondbadmin
--

ALTER SEQUENCE public.property_specs_id_seq OWNED BY public.property_specs.id;


--
-- Name: saved_properties; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.saved_properties (
    id uuid NOT NULL,
    property_id uuid NOT NULL,
    user_id character varying(128) NOT NULL,
    notes text,
    created_at timestamp with time zone
);


ALTER TABLE public.saved_properties OWNER TO maisondbadmin;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.user_roles (
    id uuid NOT NULL,
    user_id character varying(128) NOT NULL,
    role_type character varying(10) NOT NULL,
    created_at timestamp with time zone,
    CONSTRAINT valid_role_types CHECK (((role_type)::text = ANY ((ARRAY['buyer'::character varying, 'seller'::character varying])::text[])))
);


ALTER TABLE public.user_roles OWNER TO maisondbadmin;

--
-- Name: users; Type: TABLE; Schema: public; Owner: maisondbadmin
--

CREATE TABLE public.users (
    id character varying(128) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    phone_number character varying(20)
);


ALTER TABLE public.users OWNER TO maisondbadmin;

--
-- Name: addresses id; Type: DEFAULT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.addresses ALTER COLUMN id SET DEFAULT nextval('public.addresses_id_seq'::regclass);


--
-- Name: property_details id; Type: DEFAULT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_details ALTER COLUMN id SET DEFAULT nextval('public.property_details_id_seq'::regclass);


--
-- Name: property_features id; Type: DEFAULT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_features ALTER COLUMN id SET DEFAULT nextval('public.property_features_id_seq'::regclass);


--
-- Name: property_media id; Type: DEFAULT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_media ALTER COLUMN id SET DEFAULT nextval('public.property_media_id_seq'::regclass);


--
-- Name: property_specs id; Type: DEFAULT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_specs ALTER COLUMN id SET DEFAULT nextval('public.property_specs_id_seq'::regclass);


--
-- Data for Name: addresses; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.addresses (id, property_id, house_number, street, city, postcode, latitude, longitude) FROM stdin;
1	a4bfe581-e6a1-40bf-9b30-81f795897fe4	119	Wood Lane	London	W12 7ED	51.5120744	-0.225292
2	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	10	Downing St	London	SW1A 2AA	\N	\N
3	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	4	Westerfield Road	London	N15 5LA	51.582718	-0.07435433835758723
7	f12936bd-ecf9-4f71-8cf5-7d003c078e69	61	Beddington Gardens	London	SM5 3HL	51.3578377	-0.1580996
11	c45ceaa3-7c64-48db-ad80-f224d079dfe9	160	Aldersgate Street	London	EC1A 4HT	\N	\N
14	b0f992b7-669f-4ee4-be06-ef5df0c541fb	15	Lakeside Crescent	London	EN4 8QH	51.644187900000006	-0.15224933037338423
16	7e0aae2c-b274-481f-a676-349a177c33f8	66	Sheldon Avenue	London	N6 4JT	51.578966199999996	-0.15844891093190228
17	f18bd329-f3f5-4064-91cf-712c052a501d	12	Wellington Road	London	W5 4UJ	51.4987618	-0.3113463308835636
19	842c612e-5162-4614-9829-8d32eb1a6101	11a	Montague Road	London	SE12 8LX	51.55941675	0.013533650000000001
21	5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	12	Winstanley	London	SW11 2DR	51.46536815950849	-0.17283412188335193
22	095e893e-a9ff-46ff-b32d-7ccfdc547f37	32	Clapham House	London	SW11 2DT	\N	\N
23	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	23	Stanley	London	SW2 3HE	51.39638945	-0.24533064999999998
\.


--
-- Data for Name: offer_transactions; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.offer_transactions (id, negotiation_id, offer_amount, made_by, created_at) FROM stdin;
564a8014-3abd-46bc-a624-3b44b97445f5	ee5081bd-5c43-450a-a8a2-f6e806bb69aa	1000000	OlcZjpwso8SQY2KOB0rOzyi04R93	2025-03-06 20:19:17.051174+00
1be45e49-35fa-46ef-bf0e-0e85d4a0f84c	d5f66d66-d4a3-4cef-8579-0d746db0c3a2	500000	OlcZjpwso8SQY2KOB0rOzyi04R93	2025-03-06 23:49:46.386418+00
a9e51c60-e6c1-4bef-8c99-7f81b576c79b	d5f66d66-d4a3-4cef-8579-0d746db0c3a2	550000	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 23:50:23.845773+00
\.


--
-- Data for Name: properties; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.properties (id, price, bedrooms, bathrooms, main_image_url, seller_id, created_at, last_updated, status) FROM stdin;
a4bfe581-e6a1-40bf-9b30-81f795897fe4	866000	2	2	https://maisonblobstorage.blob.core.windows.net/property-images/b7941560-7ee5-45ac-bb14-c42f954612c2.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:07:17.429781+00	2025-03-06 19:02:07.256617+00	for_sale
4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	1250000	4	6	https://maisonblobstorage.blob.core.windows.net/property-images/1b7deb77-7b1f-4973-9648-bbbb44d7c6b4.jpg	205jH1gvgFNsoMQIebFtNgmpv7F2	2025-03-06 19:10:45.104792+00	2025-03-06 19:07:58.471634+00	for_sale
f12936bd-ecf9-4f71-8cf5-7d003c078e69	594000	2	1	https://maisonblobstorage.blob.core.windows.net/property-images/b42fe030-8d1f-46b9-87f3-8645adc0ff6e.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:21:31.733903+00	2025-03-06 19:19:12.476256+00	for_sale
c45ceaa3-7c64-48db-ad80-f224d079dfe9	2700000	3	2	https://maisonblobstorage.blob.core.windows.net/property-images/0dc294e7-7b5e-45af-a35b-e57f570ec292.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:33:36.500026+00	2025-03-06 19:31:11.67552+00	for_sale
b0f992b7-669f-4ee4-be06-ef5df0c541fb	1200500	3	2	https://maisonblobstorage.blob.core.windows.net/property-images/b8847616-8718-4ee7-96e7-0de946db88e7.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:40:32.865465+00	2025-03-06 19:36:56.257745+00	for_sale
7e0aae2c-b274-481f-a676-349a177c33f8	1630000	3	1	https://maisonblobstorage.blob.core.windows.net/property-images/7b8af91c-7609-4470-b3c7-3f645f6841fb.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:50:05.486327+00	2025-03-06 19:47:39.394974+00	for_sale
f18bd329-f3f5-4064-91cf-712c052a501d	1085000	3	2	https://maisonblobstorage.blob.core.windows.net/property-images/2dc5fa8e-0f33-4b2a-a8e4-6ded2e886bc3.jpg	eTq1L4QE0fTXISF0GFgiDwttp9C2	2025-03-06 20:12:41.805192+00	2025-03-06 20:27:53.635332+00	under_offer
4d54e9f8-17eb-4bfc-84b9-90403fb3e299	359500	1	1	https://maisonblobstorage.blob.core.windows.net/property-images/48d8694b-c66e-4218-a2d3-509708e737e9.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 19:13:50.666572+00	2025-03-06 23:48:51.393965+00	under_offer
842c612e-5162-4614-9829-8d32eb1a6101	726500	2	1	https://maisonblobstorage.blob.core.windows.net/property-images/0d6e4af7-a6ca-4319-a81e-a9a4140c756d.jpg	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-07 00:49:03.599939+00	2025-03-07 00:48:59.421244+00	for_sale
5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	736000	3	2	https://maisonblobstorage.blob.core.windows.net/property-images/7f56d7ce-d3c2-4b5e-8a74-1ee952a5fbc1.jpg	kYpdJOVwFrdbjq1zjniDVoiUMfV2	2025-03-07 13:16:55.441638+00	2025-03-07 13:08:04.287973+00	for_sale
095e893e-a9ff-46ff-b32d-7ccfdc547f37	221000	4	3	https://maisonblobstorage.blob.core.windows.net/property-images/c2a5fef6-5fa6-477d-a213-011047a48b2a.jpg	kYpdJOVwFrdbjq1zjniDVoiUMfV2	2025-03-07 15:54:31.725377+00	2025-03-07 15:49:48.282492+00	for_sale
5b79fde2-16e4-4403-8d45-e5c87c8d77f6	215000	2	2	https://maisonblobstorage.blob.core.windows.net/property-images/31bcc064-ec69-4eb6-bfc3-983f661e9c6c.jpg	P4yG9EKPUIfEy5FjsXqgTSNxE1C3	2025-03-07 16:36:38.016088+00	2025-03-07 16:35:58.789223+00	for_sale
\.


--
-- Data for Name: property_details; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.property_details (id, property_id, description, construction_year, heating_type) FROM stdin;
1	a4bfe581-e6a1-40bf-9b30-81f795897fe4	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	1880	gas central
2	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	1682	gas central
3	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	Nestled on Westerfield Road in desirable North London, this charming one-bedroom flat offers the perfect blend of modern living and character. Boasting 600 square feet of thoughtfully designed space, a bright reception room, and contemporary finishes throughout. Built in 2000 with an excellent EPC rating of B, this energy-efficient home with electric heating represents exceptional value in today's market.	2000	electric
7	f12936bd-ecf9-4f71-8cf5-7d003c078e69	A rare opportunity to acquire this charming two-bedroom maisonette nestled in the sought-after Beddington Gardens in SN5. Dating back to 1920, this characterful property seamlessly blends period features with modern comforts, including gas central heating throughout. Boasting a generous 1100 square feet of living space and a delightful private garden of approximately 200 square feet, this home offers the perfect balance of indoor and outdoor living in a prime London location.	1920	gas central
11	c45ceaa3-7c64-48db-ad80-f224d079dfe9	Rarely available Victorian townhouse positioned on historic Aldersgate Street in the heart of the City. This impressive residence spans approximately 2,700 square feet of versatile living space, showcasing period features throughout its three bedrooms, two bathrooms and two elegant reception rooms. Originally constructed in 1890, the property retains much of its Victorian character while offering contemporary comforts including gas central heating. Perhaps most remarkable is the exceptionally generous 800 square foot private garden – a peaceful oasis rarely found in such a central London location, making this an extraordinary offering for discerning buyers.	1890	gas central
14	b0f992b7-669f-4ee4-be06-ef5df0c541fb	Nestled on picturesque Lakeside Crescent in London's desirable EN4 district, this captivating three-bedroom house offers the perfect blend of period charm and modern convenience. Dating from 1920, this characterful property extends to approximately 1,700 square feet of thoughtfully designed accommodation featuring two elegant reception rooms and two stylish bathrooms. The delightful 598 square foot garden provides a tranquil outdoor retreat, while the additional benefits of a garage and two dedicated parking spaces make this an exceptionally practical family home rarely available in this sought-after location.	1920	gas central
16	7e0aae2c-b274-481f-a676-349a177c33f8	Situated on tree-lined Sheldon Avenue in coveted Highgate, this exceptional three-bedroom maisonette combines period charm with practical living space. The property extends to approximately 1,200 square feet of thoughtfully arranged accommodation, featuring a generous reception room and well-appointed bathroom. Dating from 1930, this characterful residence showcases the architectural distinction of its era while offering the comforts expected by today's discerning buyers. With its prime N6 location and versatile layout, this distinctive property presents an outstanding opportunity for those seeking a home of character in one of North London's most prestigious enclaves	1930	oil
17	f18bd329-f3f5-4064-91cf-712c052a501d	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	2010	electric
19	842c612e-5162-4614-9829-8d32eb1a6101	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	2010	electric
21	5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	2005	electric
22	095e893e-a9ff-46ff-b32d-7ccfdc547f37	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	2019	solid fuel
23	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	This stunning property offers a perfect blend of modern comfort and classic charm. Located in a sought-after area, it features spacious rooms with natural light throughout. The well-appointed kitchen and elegant bathrooms have been recently updated with high-quality fixtures.	2015	solid fuel
\.


--
-- Data for Name: property_features; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.property_features (id, property_id, has_garden, garden_size, parking_spaces, has_garage) FROM stdin;
1	a4bfe581-e6a1-40bf-9b30-81f795897fe4	t	250	2	t
2	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	t	150	0	f
3	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	f	\N	0	f
7	f12936bd-ecf9-4f71-8cf5-7d003c078e69	t	200	0	f
11	c45ceaa3-7c64-48db-ad80-f224d079dfe9	t	800	0	f
14	b0f992b7-669f-4ee4-be06-ef5df0c541fb	t	598	2	t
16	7e0aae2c-b274-481f-a676-349a177c33f8	f	\N	0	f
17	f18bd329-f3f5-4064-91cf-712c052a501d	t	500	2	t
19	842c612e-5162-4614-9829-8d32eb1a6101	f	\N	0	f
21	5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	t	300	399	t
22	095e893e-a9ff-46ff-b32d-7ccfdc547f37	t	300	2	t
23	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	f	400	2	f
\.


--
-- Data for Name: property_media; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.property_media (id, property_id, image_url, image_type, display_order) FROM stdin;
1	a4bfe581-e6a1-40bf-9b30-81f795897fe4	https://maisonblobstorage.blob.core.windows.net/property-images/b7941560-7ee5-45ac-bb14-c42f954612c2.jpg	main	0
2	a4bfe581-e6a1-40bf-9b30-81f795897fe4	https://maisonblobstorage.blob.core.windows.net/property-images/43bdd8e2-5c31-4be1-94bb-4d1ec7dd85d6.jpg	interior	1
3	a4bfe581-e6a1-40bf-9b30-81f795897fe4	https://maisonblobstorage.blob.core.windows.net/property-images/43b487c7-85b2-411d-8b7a-f5de5379b395.jpg	interior	2
4	a4bfe581-e6a1-40bf-9b30-81f795897fe4	https://maisonblobstorage.blob.core.windows.net/property-images/bc759f6d-c817-40a2-a94a-c9d388f161e8.jpg	interior	3
5	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	https://maisonblobstorage.blob.core.windows.net/property-images/1b7deb77-7b1f-4973-9648-bbbb44d7c6b4.jpg	main	0
6	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	https://maisonblobstorage.blob.core.windows.net/property-images/4773296d-cfac-4106-927d-0491bb0f5cfd.jpg	interior	1
7	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	https://maisonblobstorage.blob.core.windows.net/property-images/83a61e3f-908a-4aa4-b99a-81c4b0f69479.jpg	interior	2
8	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	https://maisonblobstorage.blob.core.windows.net/property-images/dfcd34a5-d7be-44b8-8951-c035d2475fed.jpg	interior	3
9	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	https://maisonblobstorage.blob.core.windows.net/property-images/5932e50b-aa30-49bb-8ad6-76c420f7748f.jpg	interior	4
10	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	https://maisonblobstorage.blob.core.windows.net/property-images/48d8694b-c66e-4218-a2d3-509708e737e9.jpg	main	0
11	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	https://maisonblobstorage.blob.core.windows.net/property-images/08dd6312-adc9-4e1d-85ea-b460aedd5c96.jpg	interior	1
12	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	https://maisonblobstorage.blob.core.windows.net/property-images/7c148880-293c-42a2-938b-5667aa4d6d1d.jpg	interior	2
13	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	https://maisonblobstorage.blob.core.windows.net/property-images/ff6f38ca-f063-4495-8f5d-89ba26299a27.jpg	interior	3
17	f12936bd-ecf9-4f71-8cf5-7d003c078e69	https://maisonblobstorage.blob.core.windows.net/property-images/b42fe030-8d1f-46b9-87f3-8645adc0ff6e.jpg	main	0
18	f12936bd-ecf9-4f71-8cf5-7d003c078e69	https://maisonblobstorage.blob.core.windows.net/property-images/7445b2f4-148f-4878-a7e8-eac2087a0c3a.jpg	interior	1
19	f12936bd-ecf9-4f71-8cf5-7d003c078e69	https://maisonblobstorage.blob.core.windows.net/property-images/45ed6635-96c7-468b-aa5d-c86bdc98a135.jpg	interior	2
20	f12936bd-ecf9-4f71-8cf5-7d003c078e69	https://maisonblobstorage.blob.core.windows.net/property-images/a920727b-f2ed-4f6c-82a6-6765754181f5.jpg	interior	3
21	f12936bd-ecf9-4f71-8cf5-7d003c078e69	https://maisonblobstorage.blob.core.windows.net/property-images/216cc6c8-fb71-465f-aaac-e05c11d20bd5.jpg	interior	4
29	c45ceaa3-7c64-48db-ad80-f224d079dfe9	https://maisonblobstorage.blob.core.windows.net/property-images/0dc294e7-7b5e-45af-a35b-e57f570ec292.jpg	main	0
30	c45ceaa3-7c64-48db-ad80-f224d079dfe9	https://maisonblobstorage.blob.core.windows.net/property-images/5e86a498-fb4f-444a-980c-0632a10ca7ed.jpg	interior	1
31	c45ceaa3-7c64-48db-ad80-f224d079dfe9	https://maisonblobstorage.blob.core.windows.net/property-images/cf21888a-c991-4d7a-9354-54ef71a67552.jpg	interior	2
32	c45ceaa3-7c64-48db-ad80-f224d079dfe9	https://maisonblobstorage.blob.core.windows.net/property-images/915cb8e8-ea7b-4e52-b235-94361d612d40.jpg	interior	3
33	c45ceaa3-7c64-48db-ad80-f224d079dfe9	https://maisonblobstorage.blob.core.windows.net/property-images/98bae8eb-15fd-41ce-9c09-3cb2e434c800.jpg	interior	4
36	b0f992b7-669f-4ee4-be06-ef5df0c541fb	https://maisonblobstorage.blob.core.windows.net/property-images/b8847616-8718-4ee7-96e7-0de946db88e7.jpg	main	0
37	b0f992b7-669f-4ee4-be06-ef5df0c541fb	https://maisonblobstorage.blob.core.windows.net/property-images/c09711d9-c24d-4f39-ae63-3264a79ee79a.jpg	interior	1
38	b0f992b7-669f-4ee4-be06-ef5df0c541fb	https://maisonblobstorage.blob.core.windows.net/property-images/87714d74-8414-4ed1-b435-a5f269f549fe.jpg	interior	2
39	b0f992b7-669f-4ee4-be06-ef5df0c541fb	https://maisonblobstorage.blob.core.windows.net/property-images/5f044dd8-38d0-4b19-b14a-c5dbbe84b422.jpg	interior	3
40	b0f992b7-669f-4ee4-be06-ef5df0c541fb	https://maisonblobstorage.blob.core.windows.net/property-images/2182bf35-c42b-429c-855e-da8c27139a32.jpg	interior	4
42	7e0aae2c-b274-481f-a676-349a177c33f8	https://maisonblobstorage.blob.core.windows.net/property-images/7b8af91c-7609-4470-b3c7-3f645f6841fb.jpg	main	0
43	7e0aae2c-b274-481f-a676-349a177c33f8	https://maisonblobstorage.blob.core.windows.net/property-images/dd9c34be-865f-4a3d-9227-1c7ed6883f22.jpg	interior	1
44	7e0aae2c-b274-481f-a676-349a177c33f8	https://maisonblobstorage.blob.core.windows.net/property-images/0cfa5654-dca8-4cf3-8627-b7d5730d459e.jpg	interior	2
45	7e0aae2c-b274-481f-a676-349a177c33f8	https://maisonblobstorage.blob.core.windows.net/property-images/53ca868d-574a-4588-83bc-f23418138668.jpg	interior	3
46	f18bd329-f3f5-4064-91cf-712c052a501d	https://maisonblobstorage.blob.core.windows.net/property-images/2dc5fa8e-0f33-4b2a-a8e4-6ded2e886bc3.jpg	main	0
47	f18bd329-f3f5-4064-91cf-712c052a501d	https://maisonblobstorage.blob.core.windows.net/property-images/8425b825-c367-4dcc-9937-ac543c8f4d35.jpg	interior	1
48	f18bd329-f3f5-4064-91cf-712c052a501d	https://maisonblobstorage.blob.core.windows.net/property-images/5623a972-a487-4285-9e5b-0f492f9e40f4.jpg	interior	2
49	f18bd329-f3f5-4064-91cf-712c052a501d	https://maisonblobstorage.blob.core.windows.net/property-images/b3a55366-5184-40fd-9be1-e0e70721c2bb.jpg	interior	3
55	842c612e-5162-4614-9829-8d32eb1a6101	https://maisonblobstorage.blob.core.windows.net/property-images/0d6e4af7-a6ca-4319-a81e-a9a4140c756d.jpg	main	0
56	842c612e-5162-4614-9829-8d32eb1a6101	https://maisonblobstorage.blob.core.windows.net/property-images/d6966aaa-0ceb-4af1-a839-414e9a0430aa.jpg	interior	1
57	842c612e-5162-4614-9829-8d32eb1a6101	https://maisonblobstorage.blob.core.windows.net/property-images/422e5564-045d-439f-952c-f2d98d55eacd.jpg	interior	2
58	842c612e-5162-4614-9829-8d32eb1a6101	https://maisonblobstorage.blob.core.windows.net/property-images/345af10e-9622-48e9-8f66-8dad07e0fa3f.jpg	interior	3
59	842c612e-5162-4614-9829-8d32eb1a6101	https://maisonblobstorage.blob.core.windows.net/property-images/d7e43edb-43c1-4f91-b682-a2e99c2aa197.jpg	interior	4
61	5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	https://maisonblobstorage.blob.core.windows.net/property-images/7f56d7ce-d3c2-4b5e-8a74-1ee952a5fbc1.jpg	main	0
62	095e893e-a9ff-46ff-b32d-7ccfdc547f37	https://maisonblobstorage.blob.core.windows.net/property-images/c2a5fef6-5fa6-477d-a213-011047a48b2a.jpg	main	0
63	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	https://maisonblobstorage.blob.core.windows.net/property-images/31bcc064-ec69-4eb6-bfc3-983f661e9c6c.jpg	main	0
\.


--
-- Data for Name: property_negotiations; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.property_negotiations (id, property_id, buyer_id, status, last_offer_by, created_at, updated_at, accepted_by, accepted_at, rejected_by, rejected_at, cancelled_at) FROM stdin;
ee5081bd-5c43-450a-a8a2-f6e806bb69aa	f18bd329-f3f5-4064-91cf-712c052a501d	OlcZjpwso8SQY2KOB0rOzyi04R93	accepted	OlcZjpwso8SQY2KOB0rOzyi04R93	2025-03-06 20:19:17.047397+00	2025-03-06 20:31:38.563865+00	eTq1L4QE0fTXISF0GFgiDwttp9C2	2025-03-06 20:31:38.559463+00	\N	\N	\N
d5f66d66-d4a3-4cef-8579-0d746db0c3a2	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	OlcZjpwso8SQY2KOB0rOzyi04R93	accepted	dANaGkh9c8cOxIZn0SLry4bpbGm2	2025-03-06 23:49:46.382944+00	2025-03-06 23:50:40.140164+00	OlcZjpwso8SQY2KOB0rOzyi04R93	2025-03-06 23:50:40.136955+00	\N	\N	\N
\.


--
-- Data for Name: property_specs; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.property_specs (id, property_id, bedrooms, bathrooms, reception_rooms, square_footage, property_type, epc_rating) FROM stdin;
1	a4bfe581-e6a1-40bf-9b30-81f795897fe4	2	2	2	1000	house	B
2	4e894a29-fb4a-4ff4-97cf-b7e66cb29fb0	4	6	3	1750	house	C
3	4d54e9f8-17eb-4bfc-84b9-90403fb3e299	1	1	1	600	flat	B
7	f12936bd-ecf9-4f71-8cf5-7d003c078e69	2	1	1	1100	maisonette	D
11	c45ceaa3-7c64-48db-ad80-f224d079dfe9	3	2	2	2700	house	E
14	b0f992b7-669f-4ee4-be06-ef5df0c541fb	3	2	2	1700	house	D
16	7e0aae2c-b274-481f-a676-349a177c33f8	3	1	1	1200	maisonette	D
17	f18bd329-f3f5-4064-91cf-712c052a501d	3	2	2	1500	house	B
19	842c612e-5162-4614-9829-8d32eb1a6101	2	1	1	1100	flat	B
21	5baaba41-0040-4f0b-a6b2-b4c42c0ef0da	3	2	2	1000	flat	B
22	095e893e-a9ff-46ff-b32d-7ccfdc547f37	4	3	2	300	house	B
23	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	2	2	4	399	flat	D
\.


--
-- Data for Name: saved_properties; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.saved_properties (id, property_id, user_id, notes, created_at) FROM stdin;
32602754-0219-439f-8503-bfdbccbe018f	f18bd329-f3f5-4064-91cf-712c052a501d	OlcZjpwso8SQY2KOB0rOzyi04R93	I want to buy this one! don't even need to view!	2025-03-06 20:17:45.407619+00
d8214d35-d377-41ce-aad9-f8d73c4a5569	5b79fde2-16e4-4403-8d45-e5c87c8d77f6	kYpdJOVwFrdbjq1zjniDVoiUMfV2	\N	2025-03-07 17:33:22.142876+00
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.user_roles (id, user_id, role_type, created_at) FROM stdin;
94257aa3-6ec4-4738-ba33-e02f244f0be9	pYfhnx60YHS58a8l1KGiIBUKc5X2	buyer	2025-03-06 18:59:51.41256+00
7ea64bb3-3414-4ad9-b456-aecc224e6a21	205jH1gvgFNsoMQIebFtNgmpv7F2	buyer	2025-03-06 19:02:12.026539+00
f3c210f6-09a7-4cb5-b8b9-7a0d6f361353	205jH1gvgFNsoMQIebFtNgmpv7F2	seller	2025-03-06 19:02:12.026547+00
f3ccf079-85ad-45e0-b036-b5a045f20405	dANaGkh9c8cOxIZn0SLry4bpbGm2	seller	2025-03-06 19:03:42.048537+00
bf756eb0-84a6-4ea2-b336-7fe8081d2f80	kYpdJOVwFrdbjq1zjniDVoiUMfV2	buyer	2025-03-06 19:13:50.468543+00
0e7a7eb1-955f-46cf-aea8-4e23a243151c	kYpdJOVwFrdbjq1zjniDVoiUMfV2	seller	2025-03-06 19:13:50.468552+00
db8cb003-d281-43f7-ac1b-8c70d1260fa0	Rveq43qCuVdLOFp6G82TyVF60Co2	buyer	2025-03-06 19:16:13.977996+00
de0b1d78-4b96-4848-bb5b-afcba10b7085	Rveq43qCuVdLOFp6G82TyVF60Co2	seller	2025-03-06 19:16:13.978005+00
15b7c5b3-5532-477a-818c-41b12d06c1a1	uWrqkqZguyYiRjYeJ48zYEujAIE2	seller	2025-03-06 19:31:30.804738+00
d5972ecf-7d42-441b-b1dc-e97e44fd9455	eTq1L4QE0fTXISF0GFgiDwttp9C2	seller	2025-03-06 20:10:50.268746+00
16761540-dcdc-42a5-966f-7d0b406b7e6f	jVcyhyNgmwVTPNAjas6FJ7I22dA2	buyer	2025-03-06 20:15:38.923246+00
cc063a94-1306-4434-b1f7-11fd12cc72df	OlcZjpwso8SQY2KOB0rOzyi04R93	buyer	2025-03-06 20:17:30.044794+00
10783ecb-c301-418f-82fa-eac6cb26f06b	x64rSTBhfAbg9LKryIspKSbzLxP2	buyer	2025-03-07 09:57:19.27854+00
19c917b8-1c9c-4c16-af2b-d3384a4b8bf9	x64rSTBhfAbg9LKryIspKSbzLxP2	seller	2025-03-07 09:57:19.278547+00
2f00f775-beed-44a9-ae05-5a1175dbe7fa	P4yG9EKPUIfEy5FjsXqgTSNxE1C3	buyer	2025-03-07 16:34:09.79454+00
d796a5f8-7b05-4b0e-bab3-ac515278069c	P4yG9EKPUIfEy5FjsXqgTSNxE1C3	seller	2025-03-07 16:34:09.794548+00
b7d9de7b-4ccf-4556-b6f6-582518365dcf	D46bvmpJFMXwN4766nWCoJkGVtE3	buyer	2025-03-07 17:34:09.122966+00
1a41ba7e-5953-451c-a67d-ea3720899a53	D46bvmpJFMXwN4766nWCoJkGVtE3	seller	2025-03-07 17:34:09.122975+00
6f58bff4-2062-4c9c-937e-f012ad486ab3	PWsrXSleP1cYUtNg4DKdPqJgXxz1	buyer	2025-03-07 18:15:02.701437+00
ca785ff4-15d2-4ce1-bfb0-45aa04a79c3a	PWsrXSleP1cYUtNg4DKdPqJgXxz1	seller	2025-03-07 18:15:02.701446+00
e7109c7b-1102-4f6f-81e1-71b3e54ef8c7	rBOOFKZW8lQ32kpT92ActiEeJvf1	buyer	2025-03-09 18:54:56.492936+00
6753906e-153f-425f-aa47-bad664383805	rBOOFKZW8lQ32kpT92ActiEeJvf1	seller	2025-03-09 18:54:56.492944+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: maisondbadmin
--

COPY public.users (id, first_name, last_name, email, phone_number) FROM stdin;
pYfhnx60YHS58a8l1KGiIBUKc5X2	User	User	finaltest@test.com	\N
205jH1gvgFNsoMQIebFtNgmpv7F2	Rob	Lovegrove	rob1@gmail.com	07000000000
dANaGkh9c8cOxIZn0SLry4bpbGm2	Alex	Bull	alexbull2010@hotmail.co.uk	07946532234
kYpdJOVwFrdbjq1zjniDVoiUMfV2	Tj	Amosu	oha2444@ic.ac.uk	07557258049
Rveq43qCuVdLOFp6G82TyVF60Co2	Testing	Testing	testing@testing.com	07946533433
uWrqkqZguyYiRjYeJ48zYEujAIE2	tj	amosu	tjamosu@gmail.com	07234323423
eTq1L4QE0fTXISF0GFgiDwttp9C2	Alex	Bull	newseller@seller.com	07946532299
jVcyhyNgmwVTPNAjas6FJ7I22dA2	Rob	Lovegrove	newbuyer@buyer.com	07946532456
OlcZjpwso8SQY2KOB0rOzyi04R93	Olatunji	Amosu	buyer@buyer.com	07946535555
x64rSTBhfAbg9LKryIspKSbzLxP2	nell	norman	nellie.norman+111@gmail.com	07763333333
P4yG9EKPUIfEy5FjsXqgTSNxE1C3	new	account	olatunjiamosuu@hotmail.co.uk	07123473456
D46bvmpJFMXwN4766nWCoJkGVtE3	Hannah	Jennings	hannahjbj@icloud.com	07906144442
PWsrXSleP1cYUtNg4DKdPqJgXxz1	Chris	Jennings	chrisjennings@me.com	07767702260
rBOOFKZW8lQ32kpT92ActiEeJvf1	William	Holy-Hasted	willholyhasted@gmail.com	07870467668
\.


--
-- Name: addresses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: maisondbadmin
--

SELECT pg_catalog.setval('public.addresses_id_seq', 23, true);


--
-- Name: property_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: maisondbadmin
--

SELECT pg_catalog.setval('public.property_details_id_seq', 23, true);


--
-- Name: property_features_id_seq; Type: SEQUENCE SET; Schema: public; Owner: maisondbadmin
--

SELECT pg_catalog.setval('public.property_features_id_seq', 23, true);


--
-- Name: property_media_id_seq; Type: SEQUENCE SET; Schema: public; Owner: maisondbadmin
--

SELECT pg_catalog.setval('public.property_media_id_seq', 63, true);


--
-- Name: property_specs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: maisondbadmin
--

SELECT pg_catalog.setval('public.property_specs_id_seq', 23, true);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: offer_transactions offer_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.offer_transactions
    ADD CONSTRAINT offer_transactions_pkey PRIMARY KEY (id);


--
-- Name: properties properties_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_pkey PRIMARY KEY (id);


--
-- Name: property_details property_details_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_details
    ADD CONSTRAINT property_details_pkey PRIMARY KEY (id);


--
-- Name: property_features property_features_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_features
    ADD CONSTRAINT property_features_pkey PRIMARY KEY (id);


--
-- Name: property_media property_media_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_media
    ADD CONSTRAINT property_media_pkey PRIMARY KEY (id);


--
-- Name: property_negotiations property_negotiations_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_pkey PRIMARY KEY (id);


--
-- Name: property_specs property_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_specs
    ADD CONSTRAINT property_specs_pkey PRIMARY KEY (id);


--
-- Name: saved_properties saved_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.saved_properties
    ADD CONSTRAINT saved_properties_pkey PRIMARY KEY (id);


--
-- Name: saved_properties uq_user_saved_property; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.saved_properties
    ADD CONSTRAINT uq_user_saved_property UNIQUE (property_id, user_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: addresses addresses_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT addresses_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: offer_transactions offer_transactions_made_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.offer_transactions
    ADD CONSTRAINT offer_transactions_made_by_fkey FOREIGN KEY (made_by) REFERENCES public.users(id);


--
-- Name: offer_transactions offer_transactions_negotiation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.offer_transactions
    ADD CONSTRAINT offer_transactions_negotiation_id_fkey FOREIGN KEY (negotiation_id) REFERENCES public.property_negotiations(id);


--
-- Name: properties properties_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: property_details property_details_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_details
    ADD CONSTRAINT property_details_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: property_features property_features_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_features
    ADD CONSTRAINT property_features_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: property_media property_media_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_media
    ADD CONSTRAINT property_media_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: property_negotiations property_negotiations_accepted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_accepted_by_fkey FOREIGN KEY (accepted_by) REFERENCES public.users(id);


--
-- Name: property_negotiations property_negotiations_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.users(id);


--
-- Name: property_negotiations property_negotiations_last_offer_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_last_offer_by_fkey FOREIGN KEY (last_offer_by) REFERENCES public.users(id);


--
-- Name: property_negotiations property_negotiations_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: property_negotiations property_negotiations_rejected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_negotiations
    ADD CONSTRAINT property_negotiations_rejected_by_fkey FOREIGN KEY (rejected_by) REFERENCES public.users(id);


--
-- Name: property_specs property_specs_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.property_specs
    ADD CONSTRAINT property_specs_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: saved_properties saved_properties_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.saved_properties
    ADD CONSTRAINT saved_properties_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: saved_properties saved_properties_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.saved_properties
    ADD CONSTRAINT saved_properties_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: maisondbadmin
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: FUNCTION pg_replication_origin_advance(text, pg_lsn); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_advance(text, pg_lsn) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_create(text); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_create(text) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_drop(text); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_drop(text) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_oid(text); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_oid(text) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_progress(text, boolean); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_progress(text, boolean) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_session_is_setup(); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_is_setup() TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_session_progress(boolean); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_progress(boolean) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_session_reset(); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_reset() TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_session_setup(text); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_setup(text) TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_xact_reset(); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_xact_reset() TO azure_pg_admin;


--
-- Name: FUNCTION pg_replication_origin_xact_setup(pg_lsn, timestamp with time zone); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_xact_setup(pg_lsn, timestamp with time zone) TO azure_pg_admin;


--
-- Name: FUNCTION pg_show_replication_origin_status(OUT local_id oid, OUT external_id text, OUT remote_lsn pg_lsn, OUT local_lsn pg_lsn); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_show_replication_origin_status(OUT local_id oid, OUT external_id text, OUT remote_lsn pg_lsn, OUT local_lsn pg_lsn) TO azure_pg_admin;


--
-- Name: FUNCTION pg_stat_reset(); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_stat_reset() TO azure_pg_admin;


--
-- Name: FUNCTION pg_stat_reset_shared(text); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_stat_reset_shared(text) TO azure_pg_admin;


--
-- Name: FUNCTION pg_stat_reset_single_function_counters(oid); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_stat_reset_single_function_counters(oid) TO azure_pg_admin;


--
-- Name: FUNCTION pg_stat_reset_single_table_counters(oid); Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT ALL ON FUNCTION pg_catalog.pg_stat_reset_single_table_counters(oid) TO azure_pg_admin;


--
-- Name: COLUMN pg_config.name; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(name) ON TABLE pg_catalog.pg_config TO azure_pg_admin;


--
-- Name: COLUMN pg_config.setting; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(setting) ON TABLE pg_catalog.pg_config TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.line_number; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(line_number) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.type; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(type) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.database; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(database) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.user_name; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(user_name) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.address; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(address) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.netmask; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(netmask) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.auth_method; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(auth_method) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.options; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(options) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_hba_file_rules.error; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(error) ON TABLE pg_catalog.pg_hba_file_rules TO azure_pg_admin;


--
-- Name: COLUMN pg_replication_origin_status.local_id; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(local_id) ON TABLE pg_catalog.pg_replication_origin_status TO azure_pg_admin;


--
-- Name: COLUMN pg_replication_origin_status.external_id; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(external_id) ON TABLE pg_catalog.pg_replication_origin_status TO azure_pg_admin;


--
-- Name: COLUMN pg_replication_origin_status.remote_lsn; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(remote_lsn) ON TABLE pg_catalog.pg_replication_origin_status TO azure_pg_admin;


--
-- Name: COLUMN pg_replication_origin_status.local_lsn; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(local_lsn) ON TABLE pg_catalog.pg_replication_origin_status TO azure_pg_admin;


--
-- Name: COLUMN pg_shmem_allocations.name; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(name) ON TABLE pg_catalog.pg_shmem_allocations TO azure_pg_admin;


--
-- Name: COLUMN pg_shmem_allocations.off; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(off) ON TABLE pg_catalog.pg_shmem_allocations TO azure_pg_admin;


--
-- Name: COLUMN pg_shmem_allocations.size; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(size) ON TABLE pg_catalog.pg_shmem_allocations TO azure_pg_admin;


--
-- Name: COLUMN pg_shmem_allocations.allocated_size; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(allocated_size) ON TABLE pg_catalog.pg_shmem_allocations TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.starelid; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(starelid) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staattnum; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staattnum) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stainherit; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stainherit) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanullfrac; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanullfrac) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stawidth; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stawidth) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stadistinct; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stadistinct) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stakind1; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stakind1) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stakind2; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stakind2) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stakind3; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stakind3) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stakind4; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stakind4) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stakind5; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stakind5) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staop1; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staop1) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staop2; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staop2) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staop3; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staop3) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staop4; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staop4) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.staop5; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(staop5) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stacoll1; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stacoll1) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stacoll2; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stacoll2) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stacoll3; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stacoll3) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stacoll4; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stacoll4) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stacoll5; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stacoll5) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanumbers1; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanumbers1) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanumbers2; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanumbers2) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanumbers3; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanumbers3) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanumbers4; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanumbers4) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stanumbers5; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stanumbers5) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stavalues1; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stavalues1) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stavalues2; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stavalues2) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stavalues3; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stavalues3) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stavalues4; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stavalues4) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_statistic.stavalues5; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(stavalues5) ON TABLE pg_catalog.pg_statistic TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.oid; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(oid) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subdbid; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subdbid) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subname; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subname) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subowner; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subowner) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subenabled; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subenabled) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subconninfo; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subconninfo) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subslotname; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subslotname) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subsynccommit; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subsynccommit) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- Name: COLUMN pg_subscription.subpublications; Type: ACL; Schema: pg_catalog; Owner: azuresu
--

GRANT SELECT(subpublications) ON TABLE pg_catalog.pg_subscription TO azure_pg_admin;


--
-- PostgreSQL database dump complete
--

