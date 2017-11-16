# Scripting composer tools

Utilities that extend the scripts editor interface made in python for python programers.

Add tools like:

* Buttons to run the abeille forms designer, integrated with scripting editor.
* Automatic light syntax check for python. Syntax errors are marked in the editor automatically. (pytlint integration)
* On demand python syntaxt checker (pytlint integration)
* Quick search of classes, methods and functions in a module
* Code navigator panel, outline of editing module
* Search references in module, current folder or a user selected folder
* list of running thread with interrupt functionality
* Basic Git integration (using JGit). It allows to use GitHub for our projects. Add functionality as:
  * Clone repository
  * Create local repository
  * Show changes between working folder and local repository
  * Update working folder
  * Commit to local repository
  * Diff files between working folder and local repository
  * Push to remote repository
  * Pull from remote repository
* Javadoc viewer. 
  * All gvSIG desktop javadocs
  * Java standards javadocs
  * Configurable javadoc sets
  * Preconfigured javadoc of:
    * JavaFX
    * Apache commons IO 
    * Nasa WorldWind
    * JGit
* Preview of markup texts:
  * ReStructuredText (.rst) 
  * Markdown (.md, CommonMark 0.28), usefull to preview README.md of GitHub.
* Automatic search, and fix imports:
  * Search for imports in javadoc
  * Standard gvSIG modules
  * Some standard python modules
  * Local scripts included in the same folders.
* Open file system explorer to access folders of scripts.
* Java classes search methods and paste in code.
* Integrateds specialized viewers in the editor for:
  - PDF
  - HTML
  - PNG
* Integrateds specialized editors for:
  * DBF files.
  * java properties files.
* Load layers in current gvSIG view from the project tree of the editor.
* Interactive python console embedded in the editor.
* Assistant for contronstruct 'use_plugin' statements and execute in the editor to allow inspect clases of other plugin.

Some tools are partially developed.
