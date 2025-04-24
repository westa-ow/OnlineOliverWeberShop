import logging
import math
import uuid
from datetime import datetime
import geoip2.database

import concurrent.futures

import stripe
from django.shortcuts import render, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from OnlineShop.settings import GEOIP_config
from shop.forms import User, BannerForm
from django.utils.translation import gettext as _

from shop.models import BannerLanguage, Language

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

db = settings.FIRESTORE_CLIENT
orders_ref = db.collection("Orders")
stones_ref = db.collection("Stones")
users_ref = db.collection('webUsers')
itemsRef = db.collection('item')
cart_ref = db.collection("Cart")
addresses_ref = db.collection('Addresses')
metadata_ref = db.collection('metadata')
favourites_ref = db.collection('Favourites')
single_order_ref = db.collection("Order")
promocodes_ref = db.collection('Promocodes')
used_promocodes_ref = db.collection('UsedPromocodes')
active_promocodes_ref = db.collection('ActivePromocodes')

READER = geoip2.database.Reader(GEOIP_config)

productGroups = { 'Rosalie': ['63338', '61272', '62242', '63542'], 'Vishap': ['32348', '12307', '23073'], 'Royal': ['61198', '63271', '62145'], 'Gallantry': ['32428'], 'Vulcan': ['63279'], 'Pacify': ['32400', '12399'], 'Medium': ['KS013R70', '22074', 'KS013RG70', 'KS013R40', 'KS013RG40', 'KS013RG55', 'KS013G70', 'KS013R90', 'KS013G90', 'KS013G40', 'KS013G55', 'KS013RG90', 'KS013R55'], 'Mati': ['41206', '32387', '23093', '23092', '32389', '23094', '12339', '32388', '12341', '12342'], 'Cat': ['11362'], 'Smooth': ['61186', '63265', '63262', '63263', '63264', '62130', '62133'], 'Camille': ['63339', '61273', '62243'], 'Drop': ['21018', 'S24019'], 'earring': ['22071', '62060', '22700', '22148', '22702', '62042', '22285', '21002', '22110', '22000', '62057', '22086', '22973', '62066', '62075', '22698', '22975', '22394', '22722', '22654', '22715', '62062', '22186', '22697', '22687', '22254', '62067', '22312', '22707', '22315', '22142', '22695', '22139', '22097', '62080', '22194', '22442', '62078', '22126', '21001', '21008', '22446', '22288', '22146', '22113', '22343', '22012', '22077', '22341', '22970', '22319', '22646', '21009', '22201', '22708', '22630', '62124', '21004', '22132', '21013', '22971', '22204', '22974', '22688', '62079'], 'Augusta': ['63274', '62148', '61200'], 'Glee': ['62272', '63358', '61300'], 'Nice': ['61068'], 'Charlotte': ['23088', '12280'], 'Spirit': ['63347', '62261'], 'Duo': ['41122'], 'Praise': ['23181', '12457'], 'Iris': ['63351'], 'Pearl': ['22847', '32298', 'S24016', 'S24015', '22921', '22922', '32297', 'S24014', 'S24013', '41156', '22980', '12210', '12066', '12050'], 'Nymph': ['32375', '12331', '23042'], 'Bohemia': ['12393', '12392', '23118'], 'Juventa': ['63273', '62147'], 'Florita': ['11110'], 'Earring': ['62258', '23173', '62259', '62173', '23170', '23169', '23171', '22740', '62257', '23168', '23172', '62256', '23166', '62255', '23174'], 'Clavis': ['32241', '11989', '22801'], 'Row': ['59100'], 'Legend': ['12113', '63260', '22890'], 'Little': ['32233', '11957', '32234', '11956'], 'Pleasure': ['32402'], 'Lithuanian': ['41168'], 'Boost': ['22916', '12157'], 'Hebo': ['12298', '32342'], 'Real': ['41036'], 'Breathe': ['22841'], 'Hop': ['23003'], 'Find': ['22116'], 'Splendor': ['63529', '63296', '62164', '61210'], 'Joy': ['22786', '32239', '11972'], 'Outspoken': ['12391'], 'Velvet': ['61292', '63346', '62260'], 'Close': ['32099'], 'Bro': ['12233', '22996'], 'Luster': ['41225', '23192', '12466'], 'Fun': ['22331'], 'Felicity': ['61270', '62239'], 'Eternal': ['11397', '32319', '12256'], 'Artemis': ['32384', '62152'], 'Corazina': ['22792', '11982'], 'Jik': ['41189'], 'Leaves': ['23104', '12372'], 'Tropics': ['12446'], 'Lofty': ['23200', '12476', '32430'], 'Reach': ['22389', '11523'], 'Ginkgo': ['63540', '61267', '63336', '61268', '62237'], 'Life': ['11671', '22594', '32293'], 'Anima': ['41200', '23086', '32372', '12328'], 'Emotions': ['12326'], 'Luxury': ['57004'], 'Leaf': ['58013', '22686', '11792'], 'Hang': ['62137'], 'Fence': ['32311'], 'Stick': ['22981'], 'Edge': ['63266'], 'Chara': ['58055'], 'FS': ['32291', '12185', '12187', '22931', '32290', '12186'], 'Lion': ['41203', '32379', '23090', '12338'], 'Joice': ['12023', '22821'], 'Chain': ['KS014G40', 'KS002', 'KS003', 'KS014R40', '57143', 'KS014RG40'], 'Initial': ['11850', '11844', '11854', '11846', '11837', '11852', '11830', '11848', '11833', '11831', '11847', '11840', '11841', '11845', '11855', '11832', '11836', '11851', '11853', '11838', '11839', '11835', '11843', '11834', '11842', '11849'], 'Mellow': ['23186', '12459'], 'Me': ['22892', '12115'], 'Legit': ['62125', '62126'], 'Zephyr': ['63305', '63303', '63306'], 'Amanor': ['23052'], 'Clear': ['61112'], 'Triumph': ['61138', '62081'], 'Eye': ['41205'], 'Point': ['12160', '22917'], 'Loop': ['12227', '22993'], 'Respect': ['12451'], 'it': ['56900'], 'Chaton': ['S24003', 'S24002', 'S24001'], 'Twice': ['22572'], 'Attitude': ['32356'], 'Boxy': ['41211'], 'Undo': ['32307', '12225'], 'Entitlement': ['12378'], 'Top': ['32226', '23011', '12251'], 'Junction Cross': ['12475'], 'Couple': ['32160', '11613'], 'Poly': ['12335'], 'Sunshine': ['63268', '61188', '62132', '63525'], 'Spotlight': ['63531', '61225', '62180', '63320'], 'Neptune': ['12302', '32346'], 'BlueEye': ['41204'], 'Anthosai': ['23063', '12284'], 'Own': ['22918', '32288', '12169'], 'Butterfly': ['S24017', '39102', 'S24011'], 'Statement': ['12293'], 'Sound': ['12243', '22965'], 'Brilliance': ['63252', '63215', '63222', '63253', '61179', '62117', '61125', '63218', '61180', '62115', '62116', '61124', '61154'], 'Horizon': ['41000', '41004'], 'Moon': ['11945'], 'Love': ['11703', '32224', '39104'], 'Eternita': ['63290'], 'Simple': ['63216', '11329', '11471', '11640'], 'Doggy': ['22699', '11808'], 'Kindness': ['12417', '32354', '23039'], 'Better': ['62107'], 'Halfmoon': ['23177', '12453'], 'Believe': ['11328', '61177'], 'Meriva': ['11073'], 'Fleur': ['32003', '11030', '22073', '11171'], 'Flourish': ['22913', '12153'], 'Double': ['12007', '22156', '22155', '61178', '22815'], 'Anahita': ['41193'], 'Way': ['22983', '12229'], 'Carmen': ['23095', '12345'], 'Bright': ['22112', '11076'], 'Turtle': ['41201', '23087', '32373', '12330', '12136'], 'Lauma': ['63280'], 'Compass': ['61193'], 'Classic': ['22105', '61185', '63520', 'V61185', '63259'], 'Wake': ['12267', '23024'], 'Exquisite': ['41207'], 'back': ['K0003G', 'K0002R', 'K0001R', 'K0002G', 'K0003R', 'K0001G'], 'Helios': ['12278', '32333'], 'Character': ['41198'], 'Tennis': ['32034', '22758', '11910'], 'Hold': ['32315'], 'Best': ['63528', '62136', 'V63528', '61191', '62135', '61190'], 'Passion': ['23026', '12269', '12270'], 'Fujin': ['32336'], 'Jolie': ['63225'], 'Princess': ['32248', '12079', '41065', '12032', '41064', '22834'], 'Quartet': ['63301', '61215'], 'Shahapet': ['41186'], 'Butterflower': ['23097', '12340'], 'Moxie': ['32371'], 'Origin': ['32313', '22976', '12207'], 'Apricus': ['61290'], 'Coleus Green': ['63353'], 'More': ['11330', '11148', '22164', '22295'], 'Blossom': ['32404', '32403', '32361', '32405', '32357', '32358', '32376', '32360', '32377', '32359'], 'Chandelier': ['23091'], 'Young': ['22729', '11924'], 'Torre': ['22805', '11996'], 'Prism': ['63299', '61212'], 'Mercy': ['61317'], 'Ameretat': ['32396', '12370', '23117'], 'Vote': ['62143', '61197'], 'Flower': ['59101', '11947', '22069', '22774'], 'Sunly': ['61143', '62084'], 'Monte': ['58016'], 'Polaris': ['63548'], 'Defiy': ['63343'], 'Freeze': ['12425', '23146'], 'Secret': ['12052', '22851'], 'Earth': ['23071'], 'Prerogative': ['41210'], 'Uno': ['11740', '22623'], 'Tane': ['32332', '12277'], 'Temple': ['32327'], 'Cube': ['S24004', '22606', 'S24005'], 'Pomona': ['23043'], 'Aura': ['23152', '12432'], 'Taboo': ['12276', '23037'], 'Romantic': ['12264', '41166', '23020', '32328', '12263'], 'Rings': ['11062'], 'Emesh': ['41190'], 'Meed': ['41226', '12472', '23199'], 'Cheer': ['63349', '62263'], 'Serendipity': ['63317', '62178', '61222'], 'Umay': ['41175'], 'Horae': ['23046'], 'Orbit': ['22779', '11953'], 'Port': ['32194'], 'Zest': ['63325', '61229'], 'Mini': ['22400'], 'Gaudí': ['32167', '22451', '11605', '41110', '11570', '58045', '58046', '11571', '11590', '11879', '11743'], 'Flor': ['22617', '11701'], 'Hallow': ['32426'], 'Away': ['32321', '12279', '23016', '12257'], 'Libella': ['58006'], 'Morningstar': ['63313', '61218', '62175'], 'MamaKuka': ['63315'], 'Scene': ['12259', '23018'], 'Goccina': ['22796', '11986'], 'Care': ['22934'], 'Lien': ['61313'], 'Windrose': ['63319', '62179', '61224'], 'Signature': ['23131'], 'Saint': ['62285', '61316'], 'Fire': ['23001', '12245', '32314'], 'Meadow': ['12433', '32415', '23153'], 'Tainted': ['32320'], 'Gerbera': ['32424', '23193', '12467'], 'Into': ['12230', '22991'], 'Courage': ['62123', '12253', '23013'], 'Fairy': ['61307'], 'Anchor': ['11540', '22399'], 'Virtue': ['61192', '62138'], 'Solitaire': ['41001', '61118'], 'Hermione': ['41172'], 'Star': ['S24010'], 'Power': ['22590', '11670'], 'Ukulan': ['23045', '12321'], 'Bowy': ['23004'], 'Dryad': ['32362'], 'Great': ['22672', '11757'], 'Cuore': ['23124', '41217'], 'Upside': ['22861', '12077'], 'Hathor': ['63276'], 'Twist': ['41151'], 'Change': ['41164', '23081', '41165', '32316', '23014', '12254'], 'Venus': ['63297'], 'Weave': ['32044'], 'Leafy': ['58066'], 'Indra': ['41182'], 'Damu': ['12289'], 'Solitär': ['63254', '63256', '62119', '61182', '62118', '62120'], 'Deja Vu': ['32325', '32324', '32326'], 'Nariphon': ['41196'], 'Prosper': ['32416', '12434', '23154', '11998', '22807'], 'Meliora': ['61289'], 'Skyline': ['41136', '11793'], 'Feronia': ['41177', '23057'], 'Silvanus': ['23044', '12282'], 'You': ['12292', '12116'], 'Vitae': ['11692'], 'Chance': ['23145', '12424'], 'Pure': ['63270', '63210', '63211', '62144', '61109'], 'Expression': ['11077'], 'Orient': ['11951', '32270', '22885', '22777'], 'Papilio': ['62278'], 'Ritual': ['63309'], 'Hemera': ['61203'], 'Dauntless': ['63331', '61256', '62233'], 'Miracle': ['23180', '12456'], 'Mystique': ['63328', '61242', '62213'], 'Chasca': ['62197'], 'Voila': ['22817'], 'Marshmallow': ['23126'], 'Rabbit': ['41202', '32386', '12329', '23085', '32374'], 'Kudos': ['32427'], 'Moment': ['32399'], 'Bun': ['12025', '22832'], 'Prestige': ['11200', '32057'], 'Asterlove': ['23159', '12439'], 'Utopia': ['23096'], 'large': ['22206'], 'Soriso': ['32353', '23069'], 'Sanctuary': ['63342'], 'Symphony': ['12426', '23147'], 'Up': ['22998'], 'Good': ['23022', '23023'], 'Rapunzel': ['41214'], 'Fantasia': ['63357', '62271', '61299'], 'Flow': ['32251', '22845', '12049'], 'RoyalDrop': ['61199', '62146'], 'Foursquare': ['63231', '61135'], 'Fiorellino': ['58048'], 'Pear': ['61148', '62089'], 'Flexibility': ['23116', '12390'], 'Heartbeat': ['12419', '23144'], 'Tree': ['11973', '22787'], 'Nexus': ['32406', '23141'], 'MyHeart': ['32249'], 'Saiph': ['63547'], 'Freak': ['12262', '32323'], 'Sinless': ['62284', '61315'], 'Beautify': ['12226', '22985', '32308', '22987'], 'Extase': ['22731', '11882', '11883'], 'Down': ['32026'], 'Villa': ['11337', '22304'], 'There': ['22896', '12119'], 'Deify': ['61284'], 'Diamond': ['11025', '22066'], 'Maria': ['63545'], 'Arista': ['12320'], 'Waterfall': ['23076'], 'Brilli': ['22364', '22363'], 'Alma': ['12395'], 'Tres': ['63519'], 'Fond': ['32158', '11615'], 'chain': ['KS015', 'KS004', 'KS001'], 'Oblong': ['41216'], 'Jump': ['23028', '23027'], 'Freedom': ['12288', '41208', '23098', '12373'], 'Romana': ['23058'], 'Links': ['41161', '41163', '41162'], 'Fiesta': ['22158'], 'Open': ['12396', '11861'], 'Blush': ['63352'], 'Music': ['11942', '22771', '22770'], 'Why': ['63247'], 'Metsaema': ['12297', '32341'], 'Timeless': ['11922', '22764'], 'Lucina': ['12287', '23068'], 'Soon': ['32186', '11133', '22145'], 'Distinct': ['63251', '62113', '61176'], 'Lunina': ['22793', '11983'], 'Triple Love': ['22966'], 'white': ['11010'], 'Whorl': ['58052'], 'ApamNapat': ['12367'], 'Lover': ['32294'], 'Posh': ['63356', '62268', '61296'], 'Cara': ['61312'], 'Azalea': ['63355', '62266', '61294'], 'DreamCatcher': ['62188', '61251'], 'Dance': ['31000', '31001'], 'Genuine': ['63258', '62121', '62122', '61184', '61183'], 'Wispy': ['12221', '22988', '32304', '32306', '12224'], 'Soul': ['63332', '62234', '61255', '63539'], 'Like': ['32302'], 'Eddy': ['32414'], 'Composition': ['11078'], 'Cleopatra': ['63284'], 'Single': ['22096', '11056'], 'Synthia': ['61278', '62250'], 'Kiss': ['32181'], 'Botany': ['23189', '12463'], 'Divide': ['32022'], 'Maia': ['63295'], 'Sheer': ['61319'], 'Guardian': ['62212', '63329', '63537'], 'Florescence': ['12435', '32417', '23155'], 'Smash': ['23196', '12471'], 'Maya': ['62254', '63362', '61280'], 'Precioso': ['32253', '22866'], 'Grey': ['31003'], 'Pearly': ['22183', '41051'], 'Karma': ['62168', '63302', '61282'], 'Coqui': ['11744', '22647', '11745'], 'Viridios': ['12305'], 'Heart': ['S24008', 'S24009', '11616', '12158'], 'Glory': ['12021', '22819'], 'Sagrada': ['11575', '11816', '11873'], 'Demeter': ['12281'], 'Focus': ['22925', '12180'], 'Giant': ['11512', '22379'], 'Esteem': ['12261', '32322'], 'Libertá': ['23100', '12375', '32391'], 'Loving': ['63291'], 'Water': ['63267', '63524', '61187', '62131'], 'Halo': ['63278', '61201'], 'Dryads': ['63275'], 'Wishful': ['23007', '12247'], 'Agni': ['41191'], 'Link': ['32049'], 'Theatrical': ['12403', '32401', '23109'], 'Rush': ['12265', '23021'], 'Crescent': ['63314', '62176', '61219'], 'Cushy': ['12480', '23203'], 'Target': ['12234', '32312', '22997'], 'Oceanides': ['23080', '12308', '32363'], 'Starfish': ['11074', '32033', '22111', '11138', '11137', '11897'], 'Freesia': ['58064'], 'Mix Tape': ['32331'], 'Furrin': ['62209'], 'Clamp': ['22937'], 'Wheely': ['63241', '61136'], 'Pontus': ['63287'], 'Run': ['12268', '23025'], 'Core': ['12209'], 'Lush': ['61302', '63360', '62274'], 'Plutos': ['12332'], 'Dashing': ['62215', '61263'], 'Medeina': ['41167'], 'Again': ['12266', '12206'], 'Drive': ['12193', '41159'], 'Favour': ['11534'], 'Catch': ['61142', '62083'], 'Gaudi': ['11825', '12012', '12011', '32212', '12010', '11826'], 'Reason': ['12252', '23012'], 'Dream': ['62264', '61293'], 'Delite': ['22759', '11974', '11911'], 'Pik': ['12427', '23148'], 'Rain': ['11210', '22199'], 'Smitten': ['12197', '32300'], 'PachaMama': ['61232'], 'Cronus': ['41169'], 'Nobly': ['23158', '58050', '12438'], 'Luminous': ['12449'], 'Relate': ['63238'], 'Step': ['63239', '61153', '63527', '63522'], 'Diana': ['23075'], 'Right': ['12380', '32410', '23132'], 'Tender': ['61126'], 'Meliae': ['41195'], 'Satin': ['63348', '62262'], 'Mix': ['12273'], 'Unique': ['23149', '12428'], 'Varuna': ['12316', '23074'], 'Lucent': ['11619', '11618', '32162', '22559'], 'River': ['12248', '23008'], 'Imperial': ['63250', '63249'], 'Twilight': ['12429'], 'Enter': ['22928', '22929'], 'Miara': ['12304', '23078'], 'Duchesse': ['62104', '63246', '61168'], 'Roma': ['12322'], 'Mariposa': ['63530', '62167', '61213'], 'Glint': ['32292', '12188', '22938'], 'Hero': ['11898', '22747'], 'Carpel': ['58060'], 'Tell': ['22979'], 'Less': ['32030'], 'Style': ['11749', '22651'], 'Concept': ['11993', '22802'], 'Pluto': ['63285'], 'Atlas': ['62157'], 'Keylove': ['12171'], 'Sense': ['22982'], 'Oasis': ['63341', '61279', '62251'], 'Blessing': ['63300'], 'Anito': ['63298', '61211', '62165'], 'Breath': ['12042'], 'Alegra': ['22872', '12126'], 'Full Heart': ['22091', '11024'], 'Terra': ['41187'], 'Finest': ['23162'], 'Mihr': ['23049'], 'Blinky': ['32232'], 'Stunning': ['32247', '12034'], 'Show': ['12404', '23142'], 'Trust': ['41209', '32006', '32005', '23099', '12374', '11273'], 'Delight': ['32393', '12377', '23102'], 'Idea': ['12406'], 'Prayer': ['23019', '12260'], 'Fame': ['63345', '62225', '32225', '61252'], 'People': ['23031', '23041', '12271'], 'Triad': ['61214', '61241'], 'Grid': ['12133'], 'Daydream': ['12181'], 'Penghou': ['41185'], 'Kodama': ['41171'], 'Caroline': ['63340', '63543', '62246'], 'Vesta': ['63293'], 'XL': ['22207'], 'Loco': ['32252', '12313'], 'Sweets': ['23151', '12431'], 'Learn': ['32272', '22895'], 'Coast': ['22396', '11536'], 'Cameo': ['11230'], 'Viola': ['S24018'], 'Panorama': ['12242', '22999'], 'Edelweiss': ['11819'], 'Expand': ['22756', '11908'], 'Merge': ['11894'], 'Pixie': ['32343', '12299'], 'Say': ['32301', '12205'], 'Towards': ['32411', '23040'], 'Tolerance': ['32408'], 'Treat': ['32279'], 'Just': ['22604', '11685'], 'Rainbow': ['22846', '32116', '11395', '12051', '32246'], 'Vow': ['62281', '61309'], 'United': ['12004', '22813'], 'Connected': ['32296'], 'Lobelia': ['62270', '63550', '61298'], 'Asterie': ['62200'], 'Ring': ['57141'], 'Choice': ['32008', '12384'], 'Tropfen': ['11022'], 'Libya': ['63283'], 'Izanami': ['23083', '12324', '32378'], 'Renown': ['12478'], 'Cherry': ['12443'], 'Belladonna': ['63312'], 'Achive': ['61195', '62141'], 'Baia': ['63248', '61171', '62109'], 'Speak': ['12045', '22871'], 'Kingly': ['22694'], 'Rakapila': ['41178'], 'Astral': ['12454', '23178'], 'Universe': ['32014', '23107', '12415'], 'Message': ['12002'], 'Elissa': ['61202'], 'ZigZag': ['12319'], 'Closer': ['32286', '12154'], 'Closed': ['11769'], 'Aglow': ['23188', '41224', '12462'], 'Icy': ['23184'], 'Newy': ['61144', '62085'], 'Persephone': ['23056', '61204'], 'Jasmine': ['41212'], 'Sweet': ['22776', '22070'], 'Ardour': ['12448'], 'Eccentric': ['12386'], 'Nightsky': ['22936'], 'Enchanted': ['61231'], 'Suadela': ['23089'], 'Mayari': ['23082', '12369'], 'Dangle': ['11788', '32200'], 'TwoCats': ['12194'], 'Windfall': ['63318', '61223', '62224'], 'Tiana': ['41213'], 'Fish': ['32334'], 'Amaterasu': ['32344', '12300'], 'Call': ['22897', '12120', '32274'], 'Doubleheart': ['11858'], 'Cherish': ['61283'], 'Relax': ['32228', '22750', '11903'], 'Cybele': ['41173'], 'Lilith': ['63359', '62273', '61301'], 'Planet': ['11410'], 'Promise': ['63344'], 'Treasure': ['12095', '32250'], 'Esostre': ['41199'], 'Ladybug': ['61260', '11182', '62231'], 'Muse': ['61205'], 'Titanic': ['12134'], 'Palmtree': ['63316', '61221', '62223'], 'Shadow': ['32317'], 'Sinann': ['23140', '12309'], 'Peak': ['22728', '11881'], 'Saiph small': ['63549'], 'Benefit': ['62134', '61189', '63526'], 'Comfort': ['62071', '63521'], 'Cloud': ['22911', '12150'], 'Turn': ['22412'], 'Unica': ['62108'], 'Dual': ['22417'], 'Gentle': ['61318'], 'External': ['11804'], 'Diez': ['62150'], 'Prezzy': ['12203'], 'Twig': ['58061'], 'Beam': ['22960', '12190'], 'Sarruma': ['12290'], 'Art': ['11714', '11875', '11713'], 'Reina': ['61167', '62102'], 'Radio': ['32287'], 'Nereids': ['23047'], 'Plain': ['32050', '32222'], 'Fine': ['32105', 'KS012R40', 'KS012G55', 'KS012R55', '11353', 'KS012G40', 'KS012RG55', 'KS012RG40'], 'Luna': ['11765'], 'Bone': ['11667'], 'Balance': ['61196', '63269', '62142'], 'MamaZara': ['62192'], 'Lempo': ['63272'], 'Peace': ['23070', '12294'], 'Koli': ['61308', '62280'], 'Select': ['41160'], 'Loyal': ['23115'], 'Ariel': ['41215'], 'Wintertime': ['32425', '12469', '23195'], 'Luxe': ['41227', '23201', '12477'], 'Minerva': ['63277'], 'MamaCocha': ['62191'], 'Liberty': ['63330', '62228', '61257'], 'Maple': ['12468', '23194'], 'Place': ['22203'], '36': ['21014'], 'South': ['32091'], 'Inner': ['61150', '62090'], 'Now': ['22837'], 'True': ['11123', '61147', '32295'], 'Asclepius': ['32380'], 'Low': ['23119'], 'MonaLisa': ['12291'], 'Silent': ['12336'], 'Decorate': ['23002'], 'Rose': ['58019'], 'Horseshoe': ['62235', '61208'], 'Lilium': ['58054'], 'Next': ['32173'], 'Touch': ['12076'], 'Skimmer': ['58056'], 'Polestar': ['63308', '61217'], 'Pearling': ['12161'], 'Sail': ['22781'], 'Joker': ['41219', '23160'], 'Repose': ['32397'], 'Apam': ['32351', '12303'], 'Infinity': ['63029', '61092'], 'Develop': ['11902', '22749'], 'Purity': ['63361', '61303', '62275'], 'Affection': ['23143', '12418'], 'Number': ['11610'], 'Vida': ['11815', '32257', '12093', '22870'], 'Contact': ['63234'], 'Edellove': ['23157', '12437'], 'Perk': ['32407', '23135'], 'Flex': ['32117'], 'Tapio': ['41180'], 'Hama': ['41170'], 'Capella': ['63546'], 'Hesper': ['63282'], 'Serenity': ['62171'], 'Sheaf': ['41184'], 'Bhumi': ['41179'], 'Pen': ['57017'], 'Dignity': ['32429'], 'Moonlight': ['32318', '12255', '23015'], 'Farfallina': ['11984', '22794'], 'My': ['12094'], 'Flowers': ['58001'], 'Safeguard': ['62204', '61239'], 'Really': ['23017', '12258'], 'Diva': ['22188'], 'Class': ['11548'], 'Celum': ['12333'], 'Sleet': ['23182', '41223', '58068'], 'Quadrat': ['41181'], 'Secure': ['12460', '23187'], 'Beat': ['23036', '11126', '12275'], 'Purpose': ['12394'], 'Dahlia': ['62248', '61276'], 'Oasis long': ['62287'], 'Pensive': ['62227', '61254'], 'Luminary': ['23150', '12430'], 'AnnaPerenna': ['62183'], '12cm': ['9209', '9206', '9205'], 'Bliss': ['63304'], 'Pursue': ['12402'], 'Surround': ['32245'], 'Junction Simple': ['12473'], 'Pack': ['11677', '22599'], 'Respire': ['32394', '12413'], 'Finesse': ['61269', '62238'], 'Divers': ['11777'], 'Extra': ['41133'], 'Volturn': ['61237'], 'Aranyani': ['12314'], 'Kurozome': ['12312'], 'Family': ['61266'], 'Papillon': ['12447', '32421'], 'Dualism': ['23176', '12452'], 'Precious': ['11134', '32043'], 'Barsamin': ['32345', '12301'], 'Esoteric': ['23179', '12455'], 'Honeybee': ['12445'], 'Hidden': ['22235', '11246'], 'Odysseus': ['32382'], 'Cupid': ['12420'], 'Pleased': ['11212'], 'Signs': ['61115'], 'Visayan': ['41174'], 'Always': ['11483'], 'Mummy': ['61265'], 'Excuse': ['23130'], 'Azure': ['62201', '61240', '62211'], 'Gracious': ['32413'], 'Amo': ['11772'], 'State': ['61151', '62092'], 'Nantosuelta': ['32335'], 'Coco': ['32275'], 'Accept': ['12240'], 'Flutter': ['62279', '63551', '61306'], 'CRY': ['11236'], 'Tune': ['12239'], 'Inside': ['32001'], 'Shine': ['11997', '22806', '22733'], 'Violet': ['S24012'], 'Shore': ['22926', '12182'], 'Blind': ['23005'], 'Faunus': ['41197'], 'Company': ['12146', '22907', '32281'], 'Sun': ['11824', '32221'], 'Hail': ['58067'], 'Stellina': ['22791', '11981'], 'earrings': ['23072'], 'Private': ['41134'], 'HulaHoop': ['62149'], 'Deja': ['23032'], 'Pluma': ['11347'], 'Crossing': ['23030'], 'Local': ['32164'], 'Rank': ['32088', '11321'], 'Complex': ['22754'], 'Wurfel': ['21015'], 'Day': ['62139'], 'Sunrise': ['12053'], 'Marguerite': ['63310'], 'Pend': ['11441', '22035'], 'Spring': ['12208'], 'Wind': ['59103'], 'Ivory': ['61305', '62277'], 'Donor': ['32299'], 'Favonius': ['62158'], 'Dropping': ['23029'], 'Solar': ['22933'], 'Tendresse': ['62199', '61235'], 'Shimmer': ['11899'], 'Wildflower': ['23191', '12465'], 'Digi': ['22831'], 'Stopper': ['K0004'], 'Mulan': ['23050'], 'Juno': ['62151'], 'Forever': ['62103', '61164'], 'Hibiscus': ['62267', '61295'], 'Darling': ['11388'], 'Anemone': ['58065'], 'Sansin': ['41188'], 'Calathea Pink': ['63354'], 'Mystery': ['22778', '11952'], 'Heavenly': ['61314', '62283'], 'Edelbloom': ['12436', '23156'], 'Unity': ['61304', '62276'], 'Sublime': ['23067', '12285', '32340'], 'Animation': ['22732', '11884'], 'Success': ['62082', '61139'], 'Freehand': ['23112', '32409', '41218'], 'Volition': ['23105', '12400'], 'Destiny': ['12440'], 'Nifty': ['62170'], 'Endless': ['12237'], 'Vibe': ['23164'], 'Candor': ['32392', '23101', '12376'], 'Caring': ['12295'], 'Split': ['11990'], 'GP': ['22294'], 'Glitz': ['63538'], 'Deli': ['22783'], 'Irpitiga': ['32364'], 'Elephant': ['58047'], 'Selena': ['62162'], 'Brill': ['22329', '32109'], 'Silk': ['11058', '32017'], 'Whisper': ['61281'], 'Drape': ['22967', '12244'], 'Heaven': ['61127'], 'Estar': ['12069'], 'Posess': ['11143'], 'Highness': ['32433'], 'Ruby': ['61275', '63544', '62245'], 'Vogue': ['61264', '62214'], 'Sleet Double': ['23183'], 'Aspect': ['12201'], 'Espira': ['11999'], 'Pin': ['22628'], 'RH': ['12235'], 'Flamme': ['12423'], 'Easy': ['32207'], 'Lagoon': ['32422'], 'Plumnus': ['23061'], 'Nightshade': ['63311'], 'Compo': ['22406'], 'Daphne': ['62247'], 'Tala': ['32349'], 'Junction ': ['12474'], 'Astro': ['12017'], 'Rondo': ['22067'], 'Poseidon': ['12334'], 'Shuffle': ['12274', '32330'], 'Dive': ['62106', '61172'], 'Cross': ['61100'], 'High': ['62105'], 'Rune': ['62177'], 'Mosaic': ['23033', '12272'], 'Dangun': ['32337'], 'Mom': ['61165'], 'Moira': ['62210'], 'Cozy': ['32423', '12458', '23185'], 'Wealth': ['32431'], 'Pawy': ['11809'], 'Laurels': ['23175', '12450'], 'Gaulish': ['23053'], 'Affinity': ['62252'], 'Sevilla': ['11723'], 'Gaia': ['23059'], 'Baianai': ['23066'], 'Wonder': ['11976', '11975', '41146', '22798'], 'Majesty': ['32432'], 'Semele': ['61209'], 'Second': ['11704'], 'Mixed': ['11272', '32254'], 'Club': ['22388', '11522'], 'Silverpaw': ['62230', '61259'], 'Dusk': ['41228', '12479', '23202'], 'Fortune': ['63288'], 'Cuff Line': ['22977'], 'Under': ['22964', '12195'], 'Helix': ['12389'], 'Vivre': ['11859'], 'Outround': ['11817'], 'Hercules': ['12337'], 'Erinia': ['62206'], 'Small': ['22082'], 'Free': ['32218'], 'Zeal': ['63552', '62286'], 'Sheen': ['58062'], 'Four': ['22330'], 'Silverdog': ['61258', '62229'], 'Limit': ['22927'], 'White': ['21016'], 'Trivia': ['62156'], 'Nectar': ['23190', '12464'], 'Wintertime Skate': ['12470'], 'Soar': ['63535', '61233'], 'Galactic': ['22685', '11791'], 'Heyday': ['58069'], 'Tucky': ['12223', '22984'], 'Perfect': ['23009', '12249'], 'Frank': ['23114'], 'Cypress': ['23198'], 'Trio': ['22989'], 'Plank': ['22994', '12204'], 'Austras': ['63289'], 'Basic': ['62072'], 'Bee': ['12444', '23167'], 'Sterilization': ['V232'], 'Sky': ['22968'], 'Femme': ['23010', '12250'], 'Boreas': ['32381'], 'Flair': ['22972'], 'Bamboo': ['58063'], 'Selene': ['61288'], 'TwinHearts': ['62169'], 'Ossa': ['62159'], 'Knot': ['11593'], 'Soft': ['11216'], 'Gaudí Drac': ['22426'], 'Ceres': ['23055'], 'Soothe': ['23138'], 'Culture': ['12236'], 'Mia': ['62241'], 'Reunite': ['12414'], 'Pace': ['61141'], 'Your': ['22893'], 'Cornetto': ['12145'], 'Spell': ['41157', '22986', '12220'], 'Mind': ['11683'], 'Sylvan': ['62208'], 'Amore': ['61206'], 'Ops': ['23062'], 'Regal': ['22767'], 'Perla': ['62190'], 'Act': ['23110'], 'Ace': ['23161'], 'Label': ['32184'], 'Twisty': ['23035'], 'Day&Night': ['22990'], 'Embrace': ['12421'], 'Between': ['32058'], 'Back': ['62100'], 'Belief': ['23163'], 'Alone': ['32305'], 'Willow': ['41221'], 'Monarch': ['58058'], 'Position': ['12199'], 'Subtle': ['61137'], 'Custody': ['63541'], 'Amihan': ['23051'], 'Grace': ['62207'], 'Bacchus': ['23064'], 'Florid': ['23197'], 'Trance': ['23129'], 'Aroma': ['58049'], 'Lunar': ['22932'], 'Simply': ['61119'], 'Acting': ['23106'], 'Pearl Sissy': ['21020'], 'Glacier': ['62091'], 'Dolphin': ['39100'], 'Sea': ['11185'], 'cuff': ['22978'], 'Heely': ['12044'], 'Hearty': ['32089'], 'Elizabeth': ['12283', '23084'], 'Levity': ['23128'], 'Lovely Pearly': ['22780'], 'Ophelia': ['61271'], 'Flamingo': ['12139'], 'Panacea': ['62154'], 'Sophia': ['62244', '61274'], 'Hecate': ['32383'], 'Ranginui': ['32352'], 'Elements': ['32037'], 'Contessa': ['32063'], 'Dot': ['22258'], 'Spinner': ['62253'], 'Hoopy': ['62205'], 'Raise': ['32284'], 'Gallia': ['32347', '12306'], 'Alice': ['62249', '61277'], 'Crayons': ['63350'], 'Lovely': ['11954'], 'Dewdrop': ['62269', '61297'], 'Essenza': ['63534'], 'Crush': ['12422'], 'Izanagi': ['12315'], 'Liber': ['23048'], 'Chimera': ['62172'], 'Latitude': ['23103', '12379'], 'Silvercat': ['62232', '61261'], 'Emblem': ['22992', '12228'], 'Tinkerbell': ['61230'], 'Blue': ['11028'], 'Adruinna': ['12310'], 'Maybe': ['32271'], 'Owly': ['11725'], 'Fourleaf': ['11771'], 'Bead': ['56027'], 'Oxylus': ['12311'], 'Dragonfly': ['58057'], 'Paradiso': ['62203', '61238'], 'Roots': ['61286'], 'Calm': ['23133'], 'Castle': ['32310'], 'Switch': ['11948', '22775'], 'Kindly': ['12461'], 'Base': ['32163'], 'Slim': ['61285'], 'Sunray': ['11752'], 'Dreamy': ['12231'], 'Symphonie': ['11742'], 'Couture': ['11032'], 'Abu': ['32338'], 'Relish': ['61310'], 'Serial': ['32165'], 'Cielo': ['62087'], 'Peony': ['58053'], 'Lilac': ['23123'], 'Ball': ['22076'], 'Twinkle': ['61287'], 'Aloha': ['11318'], 'Wing': ['61102'], 'Bravo': ['61194', '62140'], 'Troya': ['23060'], 'Rosa': ['62288'], 'Pipit': ['58059'], 'Connection': ['62282'], 'Daisy': ['S24006'], 'Safe': ['61060'], 'Coin': ['12411'], 'Blast': ['11095'], 'Mother': ['61311'], 'Pole': ['12241'], 'Sijou': ['41194'], 'Dream Trio': ['62265'], 'Toro': ['11724'], 'First': ['23000'], 'Mundo': ['12196'], 'Naiades': ['23065'], 'Instant': ['32390'], 'Vayu': ['23054'], 'Trois': ['32278'], 'Faun': ['62160'], 'Unlock': ['12159'], 'Confianza': ['61166'], 'Lily': ['62155'], 'Independence': ['32398']}


countrys_shipping = {
    'Afghanistan': 8.4,
    'Åland Islands': 8.4,
    'Albania': 8.4,
    'Algeria': 8.4,
    'American Samoa': 8.4,
    'Andorra': 8.4,
    'Angola': 8.4,
    'Anguilla': 8.4,
    'Antarctica': 8.4,
    'Antigua and Barbuda': 8.4,
    'Argentina': 35,  # South America
    'Armenia': 8.4,
    'Aruba': 8.4,
    'Australia': 8.4,
    'Austria': 8.4,
    'Azerbaijan': 8.4,
    'Bahamas': 8.4,
    'Bahrain': 8.4,
    'Bangladesh': 8.4,
    'Barbados': 8.4,
    'Belarus': 8.4,
    'Belgium': 8.4,
    'Belize': 35,  # Central America
    'Benin': 8.4,
    'Bermuda': 8.4,
    'Bhutan': 8.4,
    'Bolivia': 35,  # South America
    'Bosnia and Herzegovina': 8.4,
    'Botswana': 8.4,
    'Bouvet Island': 8.4,
    'Brazil': 35,  # South America
    'British Indian Ocean Territory': 8.4,
    'Brunei': 8.4,
    'Bulgaria': 8.4,
    'Burkina Faso': 8.4,
    'Burma (Myanmar)': 8.4,
    'Burundi': 8.4,
    'Cambodia': 8.4,
    'Cameroon': 8.4,
    'Canada': 8.4,
    'Cape Verde': 8.4,
    'Cayman Islands': 8.4,
    'Central African Republic': 8.4,
    'Chad': 8.4,
    'Chile': 35,  # South America
    'China': 8.4,
    'Christmas Island': 8.4,
    'Cocos (Keeling) Islands': 8.4,
    'Colombia': 35,  # South America
    'Comoros': 8.4,
    'Congo, Dem. Republic': 8.4,
    'Congo, Republic': 8.4,
    'Cook Islands': 8.4,
    'Costa Rica': 35,  # Central America
    'Croatia': 8.4,
    'Cuba': 35,  # South America (Carib region)
    'Cyprus': 8.4,
    'Czech Republic': 8.4,
    'Denmark': 8.4,
    'Djibouti': 8.4,
    'Dominica': 8.4,
    'Dominican Republic': 35,  # Carib region
    'East Timor': 8.4,
    'Ecuador': 35,  # South America
    'Egypt': 8.4,
    'El Salvador': 35,  # Central America
    'Equatorial Guinea': 8.4,
    'Eritrea': 8.4,
    'Estonia': 8.4,
    'Ethiopia': 8.4,
    'Falkland Islands': 8.4,
    'Faroe Islands': 8.4,
    'Fiji': 8.4,
    'Finland': 8.4,
    'France': 8.4,
    'French Guiana': 8.4,
    'French Polynesia': 8.4,
    'French Southern Territories': 8.4,
    'Gabon': 8.4,
    'Gambia': 8.4,
    'Georgia': 8.4,
    'Germany': 8.4,
    'Ghana': 8.4,
    'Gibraltar': 8.4,
    'Greece': 8.4,
    'Greenland': 8.4,
    'Grenada': 8.4,
    'Guadeloupe': 8.4,
    'Guam': 8.4,
    'Guatemala': 35,  # Central America
    'Guernsey': 8.4,
    'Guinea': 8.4,
    'Guinea-Bissau': 8.4,
    'Guyana': 35,  # South America
    'Haiti': 8.4,
    'Heard Island and McDonald Islands': 8.4,
    'Honduras': 35,  # Central America
    'HongKong': 8.4,
    'Hungary': 8.4,
    'Iceland': 8.4,
    'India': 8.4,
    'Indonesia': 8.4,
    'Iran': 8.4,
    'Iraq': 8.4,
    'Ireland': 8.4,
    'Israel': 8.4,
    'Italy': 8.4,
    'Ivory Coast': 8.4,
    'Jamaica': 8.4,
    'Japan': 8.4,
    'Jersey': 8.4,
    'Jordan': 8.4,
    'Kazakhstan': 8.4,
    'Kenya': 8.4,
    'Kiribati': 8.4,
    'Dem. Republic of Korea': 8.4,
    'Kuwait': 8.4,
    'Kyrgyzstan': 8.4,
    'Laos': 8.4,
    'Latvia': 8.4,
    'Lebanon': 8.4,
    'Lesotho': 8.4,
    'Liberia': 8.4,
    'Libya': 8.4,
    'Liechtenstein': 8.4,
    'Lithuania': 8.4,
    'Luxemburg': 8.4,
    'Macau': 8.4,
    'Macedonia': 8.4,
    'Madagascar': 8.4,
    'Malawi': 8.4,
    'Malaysia': 8.4,
    'Maldives': 8.4,
    'Mali': 8.4,
    'Malta': 8.4,
    'Man Island': 8.4,
    'Marshall Islands': 8.4,
    'Martinique': 8.4,
    'Mauritania': 8.4,
    'Mauritius': 8.4,
    'Mayotte': 8.4,
    'Mexico': 8.4,
    'Micronesia': 8.4,
    'Moldova': 8.4,
    'Monaco': 8.4,
    'Mongolia': 8.4,
    'Montenegro': 8.4,
    'Montserrat': 8.4,
    'Morocco': 8.4,
    'Mozambique': 8.4,
    'Namibia': 8.4,
    'Nauru': 8.4,
    'Nepal': 8.4,
    'Netherlands': 8.4,
    'Netherlands Antilles': 8.4,
    'New Caledonia': 8.4,
    'New Zealand': 8.4,
    'Nicaragua': 35,  # Central America
    'Niger': 8.4,
    'Nigeria': 8.4,
    'Niue': 8.4,
    'Norfolk Island': 8.4,
    'Northern Ireland': 8.4,
    'Northern Mariana Islands': 8.4,
    'Norway': 8.4,
    'Oman': 8.4,
    'Pakistan': 8.4,
    'Palau': 8.4,
    'Palestinian Territories': 8.4,
    'Panama': 35,  # Central America
    'Papua New Guinea': 8.4,
    'Paraguay': 35,  # South America
    'Peru': 35,  # South America
    'Philippines': 8.4,
    'Pitcairn': 8.4,
    'Poland': 8.4,
    'Portugal': 8.4,
    'Puerto Rico': 35,  # South America (Carib region)
    'Qatar': 8.4,
    'Reunion Island': 8.4,
    'Romania': 8.4,
    'Russian Federation': 8.4,
    'Rwanda': 8.4,
    'Saint Barthelemy': 8.4,
    'Saint Kitts and Nevis': 8.4,
    'Saint Lucia': 8.4,
    'Saint Martin': 8.4,
    'Saint Pierre and Miquelon': 8.4,
    'Saint Vincent and the Grenadines': 8.4,
    'Samoa': 8.4,
    'San Marino': 8.4,
    'São Tomé and Príncipe': 8.4,
    'Saudi Arabia': 8.4,
    'Senegal': 8.4,
    'Serbia': 8.4,
    'Seychelles': 8.4,
    'Sierra Leone': 8.4,
    'Singapore': 8.4,
    'Slovakia': 8.4,
    'Slovenia': 8.4,
    'Solomon Islands': 8.4,
    'Somalia': 8.4,
    'South Africa': 8.4,
    'South Georgia and the South Sandwich Islands': 8.4,
    'South Korea': 8.4,
    'Spain': 8.4,
    'Sri Lanka': 8.4,
    'Sudan': 8.4,
    'Suriname': 35,  # South America
    'Svalbard and Jan Mayen': 8.4,
    'Swaziland': 8.4,
    'Sweden': 8.4,
    'Switzerland': 8.4,
    'Syria': 8.4,
    'Taiwan': 8.4,
    'Tajikistan': 8.4,
    'Tanzania': 8.4,
    'Thailand': 8.4,
    'Togo': 8.4,
    'Tokelau': 8.4,
    'Tonga': 8.4,
    'Trinidad and Tobago': 8.4,
    'Tunisia': 8.4,
    'Turkey': 8.4,
    'Turkmenistan': 8.4,
    'Turks and Caicos Islands': 8.4,
    'Tuvalu': 8.4,
    'Uganda': 8.4,
    'Ukraine': 8.4,
    'United Arab Emirates': 8.4,
    'United Kingdom': 8.4,
    'United States': 32,  # USA
    'Uruguay': 35,  # South America
    'Uzbekistan': 8.4,
    'Vanuatu': 8.4,
    'Vatican City State': 8.4,
    'Venezuela': 35,  # South America
    'Vietnam': 8.4,
    'Virgin Islands (British)': 8.4,
    'Virgin Islands (U.S.)': 8.4,
    'Wallis and Futuna': 8.4,
    'Western Sahara': 8.4,
    'Yemen': 8.4,
    'Zambia': 8.4,
    'Zimbabwe': 8.4
}
countrys_vat = {'Afghanistan': 0, 'Åland Islands': 0, 'Albania': 0, 'Algeria': 0, 'American Samoa': 0, 'Andorra': 0,
                'Angola': 0, 'Anguilla': 0, 'Antarctica': 0, 'Antigua and Barbuda': 0, 'Argentina': 0, 'Armenia': 0,
                'Aruba': 0, 'Australia': 0, 'Austria': 20, 'Azerbaijan': 0, 'Bahamas': 0, 'Bahrain': 0, 'Bangladesh': 0,
                'Barbados': 0, 'Belarus': 0, 'Belgium': 21, 'Belize': 0, 'Benin': 0, 'Bermuda': 0, 'Bhutan': 0,
                'Bolivia': 0, 'Bosnia and Herzegovina': 0, 'Botswana': 0, 'Bouvet Island': 0, 'Brazil': 0,
                'British Indian Ocean Territory': 0, 'Brunei': 0, 'Bulgaria': 20, 'Burkina Faso': 0,
                'Burma (Myanmar)': 0, 'Burundi': 0, 'Cambodia': 0, 'Cameroon': 0, 'Canada': 0, 'Cape Verde': 0,
                'Cayman Islands': 0, 'Central African Republic': 0, 'Chad': 0, 'Chile': 0, 'China': 0,
                'Christmas Island': 0, 'Cocos (Keeling) Islands': 0, 'Colombia': 0, 'Comoros': 0,
                'Congo, Dem. Republic': 0, 'Congo, Republic': 0, 'Cook Islands': 0, 'Costa Rica': 0, 'Croatia': 25,
                'Cuba': 0, 'Cyprus': 19, 'Czech Republic': 21, 'Denmark': 25, 'Djibouti': 0, 'Dominica': 0,
                'Dominican Republic': 0, 'East Timor': 0, 'Ecuador': 0, 'Egypt': 0, 'El Salvador': 0,
                'Equatorial Guinea': 0, 'Eritrea': 0, 'Estonia': 22, 'Ethiopia': 0, 'Falkland Islands': 0,
                'Faroe Islands': 0, 'Fiji': 0, 'Finland': 24, 'France': 20, 'French Guiana': 0, 'French Polynesia': 0,
                'French Southern Territories': 0, 'Gabon': 0, 'Gambia': 0, 'Georgia': 0, 'Germany': 19, 'Ghana': 0,
                'Gibraltar': 0, 'Greece': 24, 'Greenland': 0, 'Grenada': 0, 'Guadeloupe': 0, 'Guam': 0, 'Guatemala': 0,
                'Guernsey': 0, 'Guinea': 0, 'Guinea-Bissau': 0, 'Guyana': 0, 'Haiti': 0,
                'Heard Island and McDonald Islands': 0, 'Honduras': 0, 'HongKong': 0, 'Hungary': 27, 'Iceland': 0,
                'India': 0, 'Indonesia': 0, 'Iran': 0, 'Iraq': 0, 'Ireland': 23, 'Israel': 0, 'Italy': 22,
                'Ivory Coast': 0, 'Jamaica': 0, 'Japan': 0, 'Jersey': 0, 'Jordan': 0, 'Kazakhstan': 0, 'Kenya': 0,
                'Kiribati': 0, 'Dem. Republic of Korea': 0, 'Kuwait': 0, 'Kyrgyzstan': 0, 'Laos': 0, 'Latvia': 21,
                'Lebanon': 0, 'Lesotho': 0, 'Liberia': 0, 'Libya': 0, 'Liechtenstein': 8.1, 'Lithuania': 21,
                'Luxemburg': 0, 'Macau': 0, 'Macedonia': 0, 'Madagascar': 0, 'Malawi': 0, 'Malaysia': 0, 'Maldives': 0,
                'Mali': 0, 'Malta': 18, 'Man Island': 0, 'Marshall Islands': 0, 'Martinique': 0, 'Mauritania': 0,
                'Mauritius': 0, 'Mayotte': 0, 'Mexico': 0, 'Micronesia': 0, 'Moldova': 0, 'Monaco': 20, 'Mongolia': 0,
                'Montenegro': 0, 'Montserrat': 0, 'Morocco': 0, 'Mozambique': 0, 'Namibia': 0, 'Nauru': 0, 'Nepal': 0,
                'Netherlands': 21, 'Netherlands Antilles': 0, 'New Caledonia': 0, 'New Zealand': 0, 'Nicaragua': 0,
                'Niger': 0, 'Nigeria': 0, 'Niue': 0, 'Norfolk Island': 0, 'Northern Ireland': 0,
                'Northern Mariana Islands': 0, 'Norway': 0, 'Oman': 0, 'Pakistan': 0, 'Palau': 0,
                'Palestinian Territories': 0, 'Panama': 0, 'Papua New Guinea': 0, 'Paraguay': 0, 'Peru': 0,
                'Philippines': 0, 'Pitcairn': 0, 'Poland': 23, 'Portugal': 23, 'Puerto Rico': 0, 'Qatar': 0,
                'Reunion Island': 0, 'Romania': 19, 'Russian Federation': 0, 'Rwanda': 0, 'Saint Barthelemy': 0,
                'Saint Kitts and Nevis': 0, 'Saint Lucia': 0, 'Saint Martin': 0, 'Saint Pierre and Miquelon': 0,
                'Saint Vincent and the Grenadines': 0, 'Samoa': 0, 'San Marino': 0, 'São Tomé and Príncipe': 0,
                'Saudi Arabia': 0, 'Senegal': 0, 'Serbia': 0, 'Seychelles': 0, 'Sierra Leone': 0, 'Singapore': 0,
                'Slovakia': 20, 'Slovenia': 22, 'Solomon Islands': 0, 'Somalia': 0, 'South Africa': 0,
                'South Georgia and the South Sandwich Islands': 0, 'South Korea': 0, 'Spain': 21, 'Sri Lanka': 0,
                'Sudan': 0, 'Suriname': 0, 'Svalbard and Jan Mayen': 0, 'Swaziland': 0, 'Sweden': 25,
                'Switzerland': 8.1, 'Syria': 0, 'Taiwan': 0, 'Tajikistan': 0, 'Tanzania': 0, 'Thailand': 0, 'Togo': 0,
                'Tokelau': 0, 'Tonga': 0, 'Trinidad and Tobago': 0, 'Tunisia': 0, 'Turkey': 0, 'Turkmenistan': 0,
                'Turks and Caicos Islands': 0, 'Tuvalu': 0, 'Uganda': 0, 'Ukraine': 0, 'United Arab Emirates': 0,
                'United Kingdom': 20, 'United States': 0, 'Uruguay': 0, 'Uzbekistan': 0, 'Vanuatu': 0,
                'Vatican City State': 0, 'Venezuela': 0, 'Vietnam': 0, 'Virgin Islands (British)': 0,
                'Virgin Islands (U.S.)': 0, 'Wallis and Futuna': 0, 'Western Sahara': 0, 'Yemen': 0, 'Zambia': 0,
                'Zimbabwe': 0}

currency_dict = {
    "1": "Euro",
    "2": "Dollar"
}

groups_dict = {
    "1": "Default",
    "2": "VK3",
    "3": "GH",
    "4": "Default_USD",
    "5": "GH_USD",
}

country_dict = {
    "231": "Afghanistan",
    "244": "Åland Islands",
    "230": "Albania",
    "38": "Algeria",
    "39": "American Samoa",
    "40": "Andorra",
    "41": "Angola",
    "42": "Anguilla",
    "232": "Antarctica",
    "43": "Antigua and Barbuda",
    "44": "Argentina",
    "45": "Armenia",
    "46": "Aruba",
    "24": "Australia",
    "2": "Austria",
    "47": "Azerbaijan",
    "48": "Bahamas",
    "49": "Bahrain",
    "50": "Bangladesh",
    "51": "Barbados",
    "52": "Belarus",
    "3": "Belgium",
    "53": "Belize",
    "54": "Benin",
    "55": "Bermuda",
    "56": "Bhutan",
    "34": "Bolivia",
    "233": "Bosnia and Herzegovina",
    "57": "Botswana",
    "234": "Bouvet Island",
    "58": "Brazil",
    "235": "British Indian Ocean Territory",
    "59": "Brunei",
    "236": "Bulgaria",
    "60": "Burkina Faso",
    "61": "Burma (Myanmar)",
    "62": "Burundi",
    "63": "Cambodia",
    "64": "Cameroon",
    "4": "Canada",
    "65": "Cape Verde",
    "237": "Cayman Islands",
    "66": "Central African Republic",
    "67": "Chad",
    "68": "Chile",
    "5": "China",
    "238": "Christmas Island",
    "239": "Cocos (Keeling) Islands",
    "69": "Colombia",
    "70": "Comoros",
    "71": "Congo, Dem. Republic",
    "72": "Congo, Republic",
    "240": "Cook Islands",
    "73": "Costa Rica",
    "74": "Croatia",
    "75": "Cuba",
    "76": "Cyprus",
    "16": "Czech Republic",
    "20": "Denmark",
    "77": "Djibouti",
    "78": "Dominica",
    "79": "Dominican Republic",
    "80": "East Timor",
    "81": "Ecuador",
    "82": "Egypt",
    "83": "El Salvador",
    "84": "Equatorial Guinea",
    "85": "Eritrea",
    "86": "Estonia",
    "87": "Ethiopia",
    "88": "Falkland Islands",
    "89": "Faroe Islands",
    "90": "Fiji",
    "7": "Finland",
    "8": "France",
    "241": "French Guiana",
    "242": "French Polynesia",
    "243": "French Southern Territories",
    "91": "Gabon",
    "92": "Gambia",
    "93": "Georgia",
    "1": "Germany",
    "94": "Ghana",
    "97": "Gibraltar",
    "9": "Greece",
    "96": "Greenland",
    "95": "Grenada",
    "98": "Guadeloupe",
    "99": "Guam",
    "100": "Guatemala",
    "101": "Guernsey",
    "102": "Guinea",
    "103": "Guinea-Bissau",
    "104": "Guyana",
    "105": "Haiti",
    "106": "Heard Island and McDonald Islands",
    "108": "Honduras",
    "22": "HongKong",
    "143": "Hungary",
    "109": "Iceland",
    "110": "India",
    "111": "Indonesia",
    "112": "Iran",
    "113": "Iraq",
    "26": "Ireland",
    "29": "Israel",
    "10": "Italy",
    "32": "Ivory Coast",
    "115": "Jamaica",
    "11": "Japan",
    "116": "Jersey",
    "117": "Jordan",
    "118": "Kazakhstan",
    "119": "Kenya",
    "120": "Kiribati",
    "121": "Dem. Republic of Korea",
    "122": "Kuwait",
    "123": "Kyrgyzstan",
    "124": "Laos",
    "125": "Latvia",
    "126": "Lebanon",
    "127": "Lesotho",
    "128": "Liberia",
    "129": "Libya",
    "130": "Liechtenstein",
    "131": "Lithuania",
    "12": "Luxemburg",
    "132": "Macau",
    "133": "Macedonia",
    "134": "Madagascar",
    "135": "Malawi",
    "136": "Malaysia",
    "137": "Maldives",
    "138": "Mali",
    "139": "Malta",
    "114": "Man Island",
    "140": "Marshall Islands",
    "141": "Martinique",
    "142": "Mauritania",
    "35": "Mauritius",
    "144": "Mayotte",
    "145": "Mexico",
    "146": "Micronesia",
    "147": "Moldova",
    "148": "Monaco",
    "149": "Mongolia",
    "150": "Montenegro",
    "151": "Montserrat",
    "152": "Morocco",
    "153": "Mozambique",
    "154": "Namibia",
    "155": "Nauru",
    "156": "Nepal",
    "13": "Netherlands",
    "157": "Netherlands Antilles",
    "158": "New Caledonia",
    "27": "New Zealand",
    "159": "Nicaragua",
    "160": "Niger",
    "31": "Nigeria",
    "161": "Niue",
    "162": "Norfolk Island",
    "245": "Northern Ireland",
    "163": "Northern Mariana Islands",
    "23": "Norway",
    "164": "Oman",
    "165": "Pakistan",
    "166": "Palau",
    "167": "Palestinian Territories",
    "168": "Panama",
    "169": "Papua New Guinea",
    "170": "Paraguay",
    "171": "Peru",
    "172": "Philippines",
    "173": "Pitcairn",
    "14": "Poland",
    "15": "Portugal",
    "174": "Puerto Rico",
    "175": "Qatar",
    "176": "Reunion Island",
    "36": "Romania",
    "177": "Russian Federation",
    "178": "Rwanda",
    "179": "Saint Barthelemy",
    "180": "Saint Kitts and Nevis",
    "181": "Saint Lucia",
    "182": "Saint Martin",
    "183": "Saint Pierre and Miquelon",
    "184": "Saint Vincent and the Grenadines",
    "185": "Samoa",
    "186": "San Marino",
    "187": "São Tomé and Príncipe",
    "188": "Saudi Arabia",
    "189": "Senegal",
    "190": "Serbia",
    "191": "Seychelles",
    "192": "Sierra Leone",
    "25": "Singapore",
    "37": "Slovakia",
    "193": "Slovenia",
    "194": "Solomon Islands",
    "195": "Somalia",
    "30": "South Africa",
    "196": "South Georgia and the South Sandwich Islands",
    "28": "South Korea",
    "6": "Spain",
    "197": "Sri Lanka",
    "198": "Sudan",
    "199": "Suriname",
    "200": "Svalbard and Jan Mayen",
    "201": "Swaziland",
    "18": "Sweden",
    "19": "Switzerland",
    "202": "Syria",
    "203": "Taiwan",
    "204": "Tajikistan",
    "205": "Tanzania",
    "206": "Thailand",
    "33": "Togo",
    "207": "Tokelau",
    "208": "Tonga",
    "209": "Trinidad and Tobago",
    "210": "Tunisia",
    "211": "Turkey",
    "212": "Turkmenistan",
    "213": "Turks and Caicos Islands",
    "214": "Tuvalu",
    "215": "Uganda",
    "216": "Ukraine",
    "217": "United Arab Emirates",
    "17": "United Kingdom",
    "21": "United States",
    "218": "Uruguay",
    "219": "Uzbekistan",
    "220": "Vanuatu",
    "107": "Vatican City State",
    "221": "Venezuela",
    "222": "Vietnam",
    "223": "Virgin Islands (British)",
    "224": "Virgin Islands (U.S.)",
    "225": "Wallis and Futuna",
    "226": "Western Sahara",
    "227": "Yemen",
    "228": "Zambia",
    "229": "Zimbabwe"
}


def get_user_prices(request, email):
    """
    This function returns the user prices category
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return get_user_category(email) or ("Default", "Euro")

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # In case of multiple proxies, take the first IP
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
        response = READER.country(ip)
        country_code = response.country.iso_code
        print(country_code)
        if country_code in ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE',
                            'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']:
            return "Default", 'Euro'
        elif country_code in ['RU']:
            return "Default_High", 'Euro'
    except geoip2.errors.AddressNotFoundError:
        pass
    return "Default_USD", 'Dollar'


def get_user_session_type(request):
    """
    This function returns the user session type
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return request.user.email
    else:
        return request.session.session_key


def get_vocabulary_product_card():
    """
    This function returns the vocabulary of translated phrases
    :param request:
    :return:
    """
    return {
        "In stock": _("In stock"),
        "Less than 5 pieces left!": _("Less than 5 pieces left!"),
        "Plating Material": _("Plating Material"),
        "Stone color": _("Stone color"),
        "Size": _("Size"),
        "Quantity number has to be less than or equal to quantity number in stock or and be greater than 0": _(
            "Quantity number has to be less than or equal to quantity number in stock or and be greater than 0"),
        "Processing": _("Processing"),
        "An error occured": _("An error occured"),
        "Product successfully added to your shopping cart": _("Product successfully added to your shopping cart"),
        "Crystal color": _("Crystal color"),
        "Plating": _("Plating"),
        "Base material": _("Base material"),
        "Quantity": _("Quantity"),
        "Number of items in your cart": _("Number of items in your cart:"),
        "Subtotal": _("Subtotal"),
        "Continue shopping": _("Continue shopping"),
        "Proceed to checkout": _("Proceed to checkout"),
        "Add to cart": _("Add to cart"),
        "This item is only available for pre-order!": _("This item is only available for pre-order!"),
        "Maximum items for pre-order is 20, minimum is 1": _("Maximum items for pre-order is 20, minimum is 1"),
        "Product width": _("Product width"),
        "Product height": _("Product height"),
        "Chain length": _("Chain length"),
        "Add to favorites": _("Add to favorites"),
        "No items found": _("No items found"),
        "Current page": _("Current page"),
        "Remove from favorites": _("Remove from favorites"),
        "Copy link": _("Copy link"),
        "Copied!": _("Copied!"),
        "Reset ": _("Reset this group"),
        "Similar products": _("Similar products"),
        "Turn off the magnifying glass": _("Turn off the magnifying glass"),
        "Turn on the magnifying glass": _("Turn on the magnifying glass"),
        "Back to shop": _("Back to shop"),
        "Cart is empty": _("Cart is empty"),
        "You cant delete items during checkout. Go back to shop pages to change your cart": _("You cant delete items during checkout. Go back to shop pages to change your cart"),
        "Remove from cart": _("Remove from cart"),
        "Please enter a valid amount.": _("Please enter a valid amount."),
        "Show details": _("Show details"),
        "Hide details": _("Hide details"),
        "Name": _("Name"),
        "Image": _("Image"),
        "Description": _("Description"),
        "Price": _("Price"),
        "Summary": _("Summary"),
        "Are you sure you want to delete this address?": _("Are you sure you want to delete this address?"),
        "The address has been successfully added!": _("The address has been successfully added!"),
        "The address has been successfully updated!": _("The address has been successfully updated!"),
        "We use cookies to personalize content and improve your browsing experience. By continuing, you accept our cookie policy.": _("We use cookies to personalize content and improve your browsing experience. By continuing, you accept our cookie policy."),
        "Decline": _("Decline"),
        "Privacy Policy": _("Privacy Policy"),
        "Accept": _("Accept"),

        "Store address update error": _("Store address update error"),
        "Store address delete error": _("Store address delete error"),
        "Store address create error": _("Store address create error"),
        "Unknown error": _("Unknown error"),
        "The store address has been successfully added.": _("The store address has been successfully added."),
        "Store address with ID": _("Store address with ID"),
        "was successfully added": _("was successfully added"),
        "was successfully updated": _("was successfully updated"),
        "was successfully deleted": _("was successfully deleted"),
        "Show route": _("Show route"),
        "Please enter the address, zip / postal code, city or country.": _("Please enter the address, zip / postal code, city or country."),
        "No stores were found in the area.": _("No stores were found in the area."),
        "An error occurred while loading stores.": _("An error occurred while loading stores."),
        "Network error when loading stores.": _("Network error when loading stores."),
        "Error loading stores.": _("Error loading stores."),
        "Latitude": _("Latitude"),
        "Longitude": _("Longitude"),
        "Loading...": _("Loading..."),
        "Address": _("Address"),
        "Update": _("Update"),
        "Delete": _("Delete"),


    }


def home_page(request):
    """
    This function returns the home page of the website
    :param request:
    :return:
    """
    current_language = request.LANGUAGE_CODE
    banners_for_lang = BannerLanguage.objects.filter(
        language__code=current_language,
        banner__active=True
    ).order_by('priority')
    print(banners_for_lang)
    context = {
        'address': request.META.get('REMOTE_ADDR'),
        'banners': banners_for_lang
    }

    test_text = _("Welcome to my site.")
    email = get_user_session_type(request)

    category, currency = get_user_prices(request, email)  # For users, the currency is determined by IP

    bestseller_items = [{"name": "22697", "product_name": "Post Earrings earring", "description": "Earrings ArtTwo RH multi",
                 "price": "52.00", "category": "Post Earrings", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22697.jpg",
                 "platings": {"Default": {"stones": {"Default": {"sizes": {},
                                                                 "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22697.jpg",
                                                                 "real_name": "22697", "quantity": 89}}}}},
                {"name": "22066", "product_name": "Post Earrings Diamond", "description": "Earrings Diamond RH CRY",
                 "price": "23.00", "category": "Post Earrings", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22066R.jpg",
                 "platings": {"Rhodium": {"stones": {"Default": {"sizes": {},
                                                                 "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22066R.jpg",
                                                                 "real_name": "22066R", "quantity": 53}}}}},
                {"name": "22821", "product_name": "Earrings Joice", "description": "Earrings Joice RH aqua",
                 "price": "39.00", "category": "Earrings", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22821%20202.jpg",
                 "platings": {"Default": {"stones": {"202": {"sizes": {},
                                                             "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22821%20202.jpg",
                                                             "real_name": "22821 202", "quantity": 412}}}}},
                {"name": "22186", "product_name": "Post Earrings earring",
                 "description": "Earrings Ladybug mini RH CRY", "price": "31.00", "category": "Post Earrings",
                 "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22186.jpg",
                 "platings": {"Default": {"stones": {"Default": {"sizes": {},
                                                                 "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22186.jpg",
                                                                 "real_name": "22186", "quantity": 90}}}}},
                {"name": "22388", "product_name": "Post Earrings Club", "description": "Earrings Club RH CRY",
                 "price": "48.00", "category": "Post Earrings", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22388%20001.jpg",
                 "platings": {"Default": {"stones": {"1": {"sizes": {},
                                                           "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/22388%20001.jpg",
                                                           "real_name": "22388 001", "quantity": 40}}}}},
                {"name": "11792", "product_name": "Pendant Leaf", "description": "Pendant Leaf RH blue",
                 "price": "73.00", "category": "Pendant", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11792%20BLU.jpg",
                 "platings": {"Default": {"stones": {"BLU": {"sizes": {},
                                                             "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11792%20BLU.jpg",
                                                             "real_name": "11792 BLU", "quantity": 78}}}}},
                {"name": "11713", "product_name": "Pendant Art", "description": "Pendant Art Two RHmulti",
                 "price": "74.00", "category": "Pendant", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11713.jpg",
                 "platings": {"Default": {"stones": {"Default": {"sizes": {},
                                                                 "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11713.jpg",
                                                                 "real_name": "11713", "quantity": 61}}}}},
                {"name": "11512", "product_name": "Pendant Giant", "description": "Pendant Giant GP silver night",
                 "price": "55.00", "category": "Pendant", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11512G.jpg",
                 "platings": {"Gold": {"stones": {"Default": {"sizes": {},
                                                              "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11512G.jpg",
                                                              "real_name": "11512G", "quantity": 109}}}}},
                {"name": "11640", "product_name": "Pendant Simple", "description": "Pendant Simple RH CRY",
                 "price": "32.00", "category": "Pendant", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11640R.jpg",
                 "platings": {"Rhodium": {"stones": {"Default": {"sizes": {},
                                                                 "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/11640R.jpg",
                                                                 "real_name": "11640R", "quantity": 98}}}}},
                {"name": "23140", "product_name": "Earrings Sinann", "description": "Earrings Sinann STE GP CZ",
                 "price": "42.00", "category": "Earrings", "material": "Steel",
                 "preview_image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/23140G.jpg",
                 "platings": {"Gold": {"stones": {"Default": {"sizes": {},
                                                              "image": "https://storage.googleapis.com/flutterapp-fd5c3.appspot.com/Images/23140G.jpg",
                                                              "real_name": "23140G", "quantity": 342}}}}}]

    currency = '€' if currency == 'Euro' else '$'
    info = get_user_info(email) or {}
    sale = get_user_sale(info)
    show_quantities = info.get('show_quantities', False)
    config_data = {
        "bestseller_items": bestseller_items,
    }
    context['currency'] = currency
    context['category'] = category
    context['sale'] = sale
    context['show_quantities'] = show_quantities
    context['hello'] = test_text
    context['bestseller_items'] = bestseller_items
    context['vocabulary'] = get_vocabulary_product_card()
    context['config_data'] = config_data
    print(context['hello'])
    return render(request, 'home.html', context)


@csrf_exempt
def csp_report(request):
    """
    Processes CSP violation reports.
    Browser sends POST request with JSON content.
    """
    if request.method == "POST":
        try:
            report_data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.error("Invalid JSON in CSP report.")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Log the received offence. Here you can configure other behaviour:
        # for example, saving the report to the database or sending notifications.
        logger.info("CSP Violation Report: %s", json.dumps(report_data, indent=2))

        # Returning a response with no content
        return JsonResponse({"status": "received"}, status=204)
    else:
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)


def get_user_sale(user_info):
    """
    This function returns the sale of the user after sale transformation.
    :param user_info: user info dictionary
    :return: transformed user sale
    """
    return round((0 if "sale" not in user_info else user_info['sale']) / 100, 3) or 0


def get_user_category(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    if user:
        for user_info in user:
            user_dict = user_info.to_dict()
            return user_dict['price_category'], user_dict.get('currency', "Euro")
    else:
        return "Default", "Euro"


def get_user_info(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    for user_info in user:
        user_dict = user_info.to_dict()
        return user_dict
    return {}


def get_address_info(addressId):
    addresses = addresses_ref.where('address_id', '==', addressId).limit(1).get()
    for address in addresses:
        address_dict = address.to_dict()
        return address_dict
    return {}


def get_vat_info(address):
    return countrys_vat.get(address['country'], 0)


def get_shipping_price(address):
    return countrys_shipping.get(address['country'], 0)


def get_cart(email):
    docs = cart_ref.where('emailOwner', '==', email).stream()

    cart = []
    for doc in docs:
        doc_dict = doc.to_dict()  # Call to_dict once

        if len(doc_dict) <= 7:
            continue
        description = doc_dict.get('description', '')

        # Simplify the handling of description encoding if necessary
        safe_description = description.encode('utf-8').decode('utf-8') if description else ''

        cart_item = {
            'name': doc_dict.get('name'),
            'product_name': doc_dict.get('product_name'),
            'quantity': doc_dict.get('quantity'),
            'category': _(doc_dict.get('category', "")) if _(doc_dict.get('category')) is not None else doc_dict.get(
                'category'),
            'number': doc_dict.get('number'),
            'image_url': doc_dict.get('image_url'),
            'description': safe_description,
            'quantity_max': doc_dict.get('quantity_max'),
            'price': doc_dict.get('price'),
            'stone': doc_dict.get('stone'),
            'plating': _(doc_dict.get('plating')),
            'material': _(doc_dict.get('material')),
            'sum': str(round(doc_dict.get('price') * doc_dict.get('quantity'), 1))
        }
        cart.append(cart_item)

    return cart


def getCart(request):
    return JsonResponse({'cart': get_cart(get_user_session_type(request))})


def get_stones():
    docs = stones_ref.stream()
    stones = {}
    for doc in docs:
        data = doc.to_dict()
        if 'id' in data and 'name' in data:
            stones[data['id']] = data['name']

    return stones


def update_quantity_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_new = data.get('quantity_new')
            price = float(data.get('price'))
            email = get_user_session_type(request)  # Replace with actual user email

            cart_items = cart_ref.where('emailOwner', '==', email)

            existing_item = cart_ref.where('emailOwner', '==', email).where('name', '==', product_id).limit(1).get()

            if existing_item:
                doc_ref = existing_item[0].reference
                doc_ref.update({'quantity': quantity_new})
                return JsonResponse({'status': 'success', 'quantity': quantity_new, 'product_id': product_id,
                                     'sum': str(round((quantity_new * price), 2)), 'was_inside': 'True'})

            else:
                product = json.loads(data.get('document'))

                number_in_cart = len(cart_items.get()) + 1

                new_cart_item = {
                    'description': product['description'],
                    'stone': str(product['stone']),
                    'material': product['material'],
                    'plating': product['plating'],
                    "emailOwner": email,
                    'image_url': product['image-url'],
                    "name": product['name'],
                    "price": price,
                    "quantity": quantity_new,
                    "number": number_in_cart,
                    "product_name": product['product_name'],
                    "category": product['category'],
                    'quantity_max': product['quantity']
                }
                cart_ref.add(new_cart_item)
                return JsonResponse({'status': 'success', 'quantity': quantity_new, 'product_id': product_id,
                                     'sum': str(round((quantity_new * price), 2)), 'was_inside': 'False',
                                     'number': number_in_cart})
        except Exception as e:
            print(f"Error updating cart: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                                status=500)


    else:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)


def deleteProduct(request):
    """
    This function deletes a product from the cart
    :param request:
    :return:
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('document_id')
        if data.get('email'):
            email = data.get('email')
        else:
            email = get_user_session_type(request)
        docs = cart_ref.where('emailOwner', '==', email).where('name', '==', name).stream()
        for doc in docs:
            doc.reference.delete()

        remaining_docs = cart_ref.where('emailOwner', '==', email).order_by('number').stream()
        new_number = 1
        updated_documents = []
        for doc in remaining_docs:
            doc.reference.update({'number': new_number})
            updated_documents.append({'id': doc.to_dict().get('name', ''), 'number': new_number})
            new_number += 1

        return JsonResponse({'status': 'success', 'updated_documents': updated_documents})
    return JsonResponse({'status': 'error'}, status=400)


def update_email_in_db(old_email, new_email):
    """
    This function updates the email in the database
    :param old_email:
    :param new_email:
    :return:
    """

    # Define a mapping of collections to their respective email fields
    collection_email_fields = {
        'Cart': 'emailOwner',
        'Favourites': 'email',
        'Order': 'emailOwner',
        'Orders': 'email',
        'ActivePromocodes': 'email',
        'UsedPromocodes': 'email',
        'Addresses': 'email',
    }

    old_coupon = get_active_coupon(old_email)
    new_coupon = get_active_coupon(new_email)

    if new_coupon:
        delete_user_coupons(old_email)

    old_discount = old_coupon.get('discount', 0) / 100.0 if old_coupon else 0
    new_discount = new_coupon.get('discount', 0) / 100.0 if new_coupon else 0

    used_coupon_docs = list(
        used_promocodes_ref
        .where('coupon_code', '==', old_coupon.get('coupon_code', ''))
        .stream()
    )

    # Loop through the mapping
    for collection_name, email_field in collection_email_fields.items():
        try:
            # Reference the collection
            collection_ref = db.collection(collection_name)
            # Query for documents with the old email
            docs_to_update = collection_ref.where(email_field, '==', old_email).get()
            # Update each document with the new email
            for doc in docs_to_update:
                doc_data = doc.to_dict()

                # If the collection is Cart, let's recalculate the prices
                if collection_name == 'Cart' and 'price' in doc_data:
                    original_price = doc_data['price']
                    # Restore the original price if the old coupon is discounted
                    if old_discount > 0:
                        if new_discount > 0 or used_coupon_docs:
                            original_price = original_price / (1 - old_discount)

                    # Apply the new discount if a new coupon is available
                    if new_discount > 0:
                        updated_price = original_price * (1 - new_discount)
                    else:
                        updated_price = original_price

                    # Updating the price in the document
                    doc.reference.update({
                        'price': updated_price
                    })

                if collection_name == 'ActivePromocodes' and used_coupon_docs:
                    continue
                # Updating email in a document
                doc.reference.update({email_field: new_email})
        except Exception as e:
            # Log the error e
            print(f"Error updating {collection_name}: {str(e)}")

    return "Updated"


def serialize_firestore_document(doc):
    """
    Convert a Firestore document to a dictionary, handling DatetimeWithNanoseconds.

    Args:
        doc: Firestore document snapshot.

    Returns:
        dict: Serialized dictionary with ISO-formatted datetime strings.
    """
    doc_dict = doc.to_dict()
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            # Convert datetime to ISO format (compatible with JavaScript/JSON)
            doc_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    return doc_dict



def is_admin(user):
    """
    Test on is user an admin
    :param user:
    :return:
    """
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_tools(request, feature_name):
    if feature_name == "manage_banners":
        if request.method == "POST":
            form = BannerForm(request.POST, request.FILES)
            if form.is_valid():
                new_banner = form.save()
                return redirect('admin_tools', feature_name='manage_banners')
    email = request.user.email
    form = BannerForm()
    special = False
    if email == "specialAdmin@oliverweber.at":
        special = True

    current_language = request.GET.get('lang', request.LANGUAGE_CODE)

    banners_for_lang = BannerLanguage.objects.filter(
        language__code=current_language,
        banner__active=True
    ).order_by('priority')
    all_languages = Language.objects.all()
    context = {
        "feature_name": feature_name,
        'banners': banners_for_lang,
        'form': form,
        'special': special,
        'all_languages': all_languages,
        'current_language': current_language,
        'vocabulary': get_vocabulary_product_card(),
    }
    if feature_name == "manage_promocodes":
        context['promocodes'] = get_promo_codes()
    return render(request, 'admin_tools.html', context)


@login_required
@user_passes_test(is_admin)
def delete_users(request):
    """
    Delete users from the database
    :param request:
    :return:
    """
    if request.method == 'POST':
        try:
            # Load the user IDs from the request body
            data = json.loads(request.body)
            user_ids = data.get('userIds')

            if not user_ids:
                return JsonResponse({'status': 'error', 'message': 'No user IDs provided'}, status=400)

            emails_to_delete = []

            # Firestore has a limit of 500 operations per batch
            batch = db.batch()
            operations_count = 0

            for user_id in user_ids:
                # Query for documents with matching userId field

                docs = users_ref.where('userId', '==', int(user_id)).get()

                for doc in docs:
                    user_data = doc.to_dict()  # Convert document to dictionary
                    if 'email' in user_data:
                        emails_to_delete.append(user_data['email'])
                    doc_ref = users_ref.document(doc.id)
                    batch.delete(doc_ref)
                    operations_count += 1

                    # Commit the batch if it reaches the Firestore limit
                    if operations_count >= 500:
                        batch.commit()
                        batch = db.batch()  # Start a new batch
                        operations_count = 0

            if emails_to_delete:
                User.objects.filter(email__in=emails_to_delete).delete()

            # Commit any remaining operations in the batch
            if operations_count > 0:
                batch.commit()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def get_acc_data(email):
    """
    Fetch account data for a given email from Firestore
    :param email:
    :return:
    """
    existing_user = users_ref.where('email', '==', email).limit(1).stream()
    if existing_user:
        for user in existing_user:
            user_ref = users_ref.document(user.id)
            user_data = serialize_firestore_document(user_ref.get())
            user_info_dict = json.dumps(user_data)
            user_info_parsed = json.loads(user_info_dict)
            return user_info_dict, user_info_parsed
    return False, False


def fetch_document_name(item):
    """
    Fetch the document name for a given item
    :param item:
    :return:
    """
    if isinstance(item, str):
        item_ref = db.document(item)
    else:
        item_ref = item  # Assuming it's a document reference already
    doc = item_ref.get()
    return doc.to_dict() if doc.exists else None


def parallel_fetch_names(item_list):
    """
    Fetch document names in parallel for a list of items
    :param item_list:
    :return:
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        order_items_dict = list(executor.map(fetch_document_name, item_list))

    items = {}
    for item in order_items_dict:
        items[item.get("name")] = item
    return items


def process_items(item_list):
    """ Process items from item list with efficient fetching and error handling. """
    all_orders = parallel_fetch_names(item_list)

    names = [item for item in all_orders.keys()]

    # assuming item_list consists of item names
    name_to_item_data = fetch_items_by_names(names)
    order_items = []
    for name in names:
        item_data = name_to_item_data.get(name)
        if item_data and 'quantity' in item_data and 'price' in item_data:
            order_items.append({
                **all_orders.get(name),
                'quantity_max': item_data.get('quantity'),  # Example additional data
                'total': round(all_orders.get(name)['quantity'] * all_orders.get(name).get('price', 0), 2)
            })
    return order_items


def fetch_items_by_names(names):
    """ Fetch items by names using batched 'IN' queries to reduce the number of read operations. """
    items_ref = db.collection('item')
    name_to_item_data = {}

    # Firestore supports up to 10 items in an 'IN' query
    for i in range(0, len(names), 10):
        batch_names = names[i:i + 10]
        query_result = items_ref.where('name', 'in', batch_names).get()
        for doc in query_result:
            if doc.exists:
                name_to_item_data[doc.get('name')] = doc.to_dict()
    return name_to_item_data


def get_order(order_id):
    """
    Get order data for a given order_id
    :param order_id:
    :return:
    """
    chosenOrderRef = orders_ref.where("order_id", '==', int(order_id)).limit(1).stream()
    order = {}

    for chosenReference in chosenOrderRef:
        order = chosenReference.to_dict()
        break  # If at least one result is found, exit the loop

    # If nothing is found, search by the key `order-id`
    if not order:
        chosenOrderRef = orders_ref.where("`order-id`", '==', int(order_id)).limit(1).stream()
        for chosenReference in chosenOrderRef:
            order = chosenReference.to_dict()
            break  # If at least one result is found, exit the loop

    return order


def get_order_items(order_id):
    chosenOrderRef = orders_ref.where("`order-id`", '==', int(order_id)).limit(1).stream()
    specificOrderData = {}

    for chosenReference in chosenOrderRef:
        specificOrderData = chosenReference.to_dict()

    # Assuming you have a way to reference your 'Item' collection
    itemList = specificOrderData.get('list', [])

    order_items = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_items, itemList)
        try:
            order_items = future.result(timeout=30)  # Adding a generous timeout to see if it helps
        except Exception as e:
            print(f"Unhandled exception: {e}")
    return order_items


def get_promo_codes():
    promocodes = promocodes_ref.stream()
    promocodes_data = []

    for promocode in promocodes:
        promocodes_data.append(promocode.to_dict())

    return promocodes_data


def get_active_coupon(email):
    query = active_promocodes_ref.where('email', '==', email).limit(1).stream()

    # Receive the first coupon, if it exists
    active_coupon = next(query, None)

    if active_coupon:
        coupon_data = active_coupon.to_dict()

        # Delete fields if they are present
        coupon_data.pop('created_at', None)
        coupon_data.pop('expires_at', None)

        return coupon_data
    else:
        return {}


def active_cart_coupon(email):
    """
    Apply discount to cart items for a user with a specific email
    :param email:
    :return:
    """
    try:
        # Check if there is an active coupon for the user
        active_coupons = list(active_promocodes_ref.where('email', '==', email).stream())

        if not active_coupons:
            return JsonResponse({'status': 'error', 'message': 'No active coupons for the user'})

        # Assume that only one coupon is active (take the first one)
        active_coupon = active_coupons[0].to_dict()
        discount = active_coupon.get('discount', 0)

        if not isinstance(discount, (int, float)) or discount <= 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid active coupon'})

        discount_rate = 1 - (discount / 100.0)

        # Apply discount to items in cart
        docs = cart_ref.where('emailOwner', '==', email).stream()

        updated_cart = []
        for doc in docs:
            doc_dict = doc.to_dict()

            if 'price' in doc_dict and isinstance(doc_dict['price'], (int, float)):
                # Apply the discount to the price
                new_price = doc_dict['price'] * discount_rate

                # Updating the document in Firestore
                cart_ref.document(doc.id).update({'price': new_price})
                doc_dict['price'] = new_price  # Update locally to return the data

            updated_cart.append(doc_dict)

        return JsonResponse({
            'status': 'success',
            'message': 'Discount applied to cart items',
            'updated_cart': updated_cart
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error applying coupon: {str(e)}'})


def delete_user_coupons(email):
    try:
        # Looking for all active coupons of the user
        user_coupons = active_promocodes_ref.where('email', '==', email).stream()

        # Deleting each coupon
        for coupon in user_coupons:
            active_promocodes_ref.document(coupon.id).delete()

        return {"status": "success", "message": "All active coupons for the user have been deleted"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}


def mark_user_coupons_as_used(email):
    try:
        # Looking for all active coupons of the user
        user_coupons = list(active_promocodes_ref.where('email', '==', email).stream())

        if not user_coupons:
            print(f"There are no active coupons for the user {email}")
            return

        for coupon in user_coupons:
            coupon_data = coupon.to_dict()

            # Create a new UUID for UsedPromocodes
            new_used_coupon_id = str(uuid.uuid4())

            # Transferring the coupon to UsedPromocodes
            used_promocodes_ref.document(new_used_coupon_id).set({
                'email': email,
                'coupon_code': coupon_data.get('coupon_code'),  # Take the coupon code from the active
                'discount': coupon_data.get('discount'),  # Take the size of the discount
                'created_at': datetime.now()
            })


    except Exception as e:
        print(f"Error when transferring coupons to UsedPromocodes: {e}")


def haversine(lat1, lon1, lat2, lon2):
    # Great circle distance in km
    R = 6371.0
    a1, a2 = math.radians(lat1), math.radians(lat2)
    da = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(da/2)**2 + math.cos(a1)*math.cos(a2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))