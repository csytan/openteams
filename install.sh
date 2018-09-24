# http://charlesleifer.com/blog/using-the-sqlite-json1-and-fts5-extensions-with-python/


brew install fossil



export JQLITE="$HOME/bin/jqlite"
mkdir -p $JQLITE
cd $JQLITE


fossil clone http://www.sqlite.org/cgi/src sqlite.fossil
fossil open sqlite.fossil

curl 'https://www.sqlite.org/src/tarball/sqlite.tar.gz?ci=trunk' | tar xz
mv sqlite/* .


# Compiling SQLite with json1 and fts5
export CFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA \
-DSQLITE_ENABLE_DBSTAT_VTAB \
-DSQLITE_ENABLE_FTS3 \
-DSQLITE_ENABLE_FTS3_PARENTHESIS \
-DSQLITE_ENABLE_FTS4 \
-DSQLITE_ENABLE_FTS5 \
-DSQLITE_ENABLE_JSON1 \
-DSQLITE_ENABLE_STAT4 \
-DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
-DSQLITE_SECURE_DELETE \
-DSQLITE_SOUNDEX \
-DSQLITE_TEMP_STORE=3 \
-O2 \
-fPIC"
LIBS="-lm" ./configure --prefix=$JQLITE --enable-static --enable-shared
make
make install



# Build apsw
cd $JQLITE
git clone https://github.com/rogerbinns/apsw
cd apsw
cp ../sqlite3{ext.h,.h,.c} .
echo -e "library_dirs=$JQLITE/lib" >> setup.cfg
echo -e "include_dirs=$JQLITE/include" >> setup.cfg
LIBS="-lm" python setup.py build
