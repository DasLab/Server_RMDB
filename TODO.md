## To-do wish-list for RMDB dev

#### Code Restructure
- Migrate and clean `src/helper/*.py` to `src/util`, which overlaps with other tasks
- Write server docs and wiki

#### RESTful API
- Check and test legacy API code
- _[Less important]_ Make API fully RESTful, support for CRUD operations
- Write full **documentation** on API (currently missing)

#### Entry page visualization
- Fix barplot length problem for Lucks new RDAT format (which with variable length of rows)
- Experiment with `<canvas>` for faster heatmap rendering, especially for large (e.g. ETERNA) datasets
- Try nodejs pre-render of d3 heatmap and cache on server side, to reduce client side burden
- Integrate Eterna Data Browser here?

#### _[Less important]_ Structural Server
- Provide RNAstructure running service (currently disabled)
- Enable (and set limit) for Bootstrapping (e.g. 100x for `Fold`, 10x for `ShapeKnots`; maybe more relaxed for "core" member/accounts)
- Job management system (like `Primerize` server): UUID, long-poll AJAX update, python threading job
- Once online, pre-run all RMDB_ID entries, and cache their prediction results, and display on entry page

#### _[Less important]_ Advanced Search
- Read and understand Pablo's legacy code
- Fix it and bring back online
- Allow retrieving Construct, instead of concatenation of RDAT as a unit

#### _[Less important]_ Miscellaneous
_added by Rhiju_  
- use one of the beautiful JS PDB viewers to display data on *3D models* if user provides PDB ID or model.
- contact Sanbonmatsu lab and others to deposit their data
- update the cache settings so that browsers actually see updates
- update Latest News to have events from 2016 and 2017
– update RMDB Pubmed IDs for standardization paper — get joe’s help to update database.
- RMDB needs to move to rmdb.org or rna-map.org or `rmdb.io`
- Deposit deanonymized RDATs for RNA puzzles.
- update RMDB to include data from (sripakdeevong, 2011) paper.

### DONE
#### Secondary structure visualization:
- Integrate `Forna-2D` (http://nibiru.tbi.univie.ac.at/forna/). Use the fornac.js for front-end (https://github.com/pkerpedjiev/forna)
- ~~_[Less important]_ Provide VARNA JAR/applet (restore from old page, currently disabled); or just provide/cache a static VARNA image for quick view~~ VARNA is dead.
