## To-do wish-list for RMDB dev

#### 0. Code Restructure
- Migrate and clean `src/helper/*.py` to `src/util`, which overlaps with other tasks
- Write server docs and wiki

#### 1. Secondary structure visualization:
- Integrate `Forna-2D` (http://nibiru.tbi.univie.ac.at/forna/). Use the fornac.js for front-end (https://github.com/pkerpedjiev/forna)
- _[Less important]_ Provide VARNA JAR/applet (restore from old page, currently disabled); or just provide/cache a static VARNA image for quick view

#### 2. RESTful API
- Check and test legacy API code
- _[Less important]_ Make API fully RESTful, support for CRUD operations
- Write full **documentation** on API (currently missing)

#### 3. Entry page visualization
- Fix barplot length problem for Lucks new RDAT format (which with variable length of rows)
- Experiment with `<canvas>` for faster heatmap rendering, especially for large (e.g. ETERNA) datasets
- Try nodejs pre-render of d3 heatmap and cache on server side, to reduce client side burden
- Integrate Eterna Data Browser here?

#### 4. _[Less important]_ Structural Server
- Provide RNAstructure running service (currently disabled)
- Enable (and set limit) for Bootstrapping (e.g. 100x for `Fold`, 10x for `ShapeKnots`; maybe more relaxed for "core" member/accounts)
- Job management system (like `Primerize` server): UUID, long-poll AJAX update, python threading job
- Once online, pre-run all RMDB_ID entries, and cache their prediction results, and display on entry page

#### 5. _[Less important]_ Advanced Search
- Read and understand Pablo's legacy code
- Fix it and bring back online
- Allow retrieving Construct, instead of concatenation of RDAT as a unit