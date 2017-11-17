## To-do wish-list for RMDB dev

### Bug fix

#### RESTful API
- Check and test legacy API code
- _[Less important]_ Make API fully RESTful, support for CRUD operations
- Write full **documentation** on API (currently missing)

#### Entry page visualization
- Fix barplot length problem for Lucks new RDAT format (which with variable length of rows)
- Experiment with `<canvas>` for faster heatmap rendering, especially for large (e.g. ETERNA) datasets
- Try nodejs pre-render of d3 heatmap and cache on server side, to reduce client side burden

#### Entry management
-- contact Sanbonmatsu lab and others to deposit their data  [rhiju]
- Featured Contributor: Julius Lucks [and set up for: Karissa, Alain, molecules, etc.]
- Deposit deanonymized RDATs for RNA puzzles. [rhiju]
- update RMDB to include data from (sripakdeevong, 2011) paper. [rhiju]
- Add Sort Function to Entry Management page.
- Split Entries in to sections based on the relationship to them (Owner, Co-owner, Principal Investigator).

#### Miscellaneous
– update RMDB Pubmed IDs for standardization paper and all other papers — get joe’s help to update database.
- use one of the beautiful JS PDB viewers to display data on *3D models* if user provides PDB ID or model.
- RMDB needs to move to rmdb.org or rna-map.org or `rmdb.io`
- need to move ribokit/primerize/mapseeker licensing over to (new) ribokit server and database instead of hosted at RMDB.
- Add Email verification Function for Registration and Updata Email in Profile.
- Improve fromset display for add co-owners and principal investigator.
----------------------------------------------------------------------------------------------------------





#### _[Less important]_ Structural Server
- Provide RNAstructure running service (currently disabled)
- Enable (and set limit) for Bootstrapping (e.g. 100x for `Fold`, 10x for `ShapeKnots`; maybe more relaxed for "core" member/accounts)
- Job management system (like `Primerize` server): UUID, long-poll AJAX update, python threading job
- Once online, pre-run all RMDB_ID entries, and cache their prediction results, and display on entry page

#### _[Less important]_ Advanced Search
- Read and understand Pablo's legacy code
- Fix it and bring back online
- Allow retrieving Construct, instead of concatenation of RDAT as a unit
- Integrate Eterna Data Browser here?


### DONE
#### Secondary structure visualization:
- Integrate `Forna-2D` (http://nibiru.tbi.univie.ac.at/forna/). Use the fornac.js for front-end (https://github.com/pkerpedjiev/forna)
- ~~_[Less important]_ Provide VARNA JAR/applet (restore from old page, currently disabled); or just provide/cache a static VARNA image for quick view~~ VARNA is dead.
~~#### Code Restructure~~
~~- Migrate and clean `src/helper/*.py` to `src/util`, which overlaps with other tasks~~
~~- Write server docs and wiki~~
~~- update Latest News to have events from 2016 and 2017~~
~~### Bug fix~~
~~- submission hangs if authors is not specified.~~
~~#### Entry management~~
~~- entry management system ~~
~~### Bug fix~~
~~- update the cache settings so that browsers actually see updates~~
