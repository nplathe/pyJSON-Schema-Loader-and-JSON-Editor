# Usage of pyJSON

## The first start

After [installation](installation), when starting pyJSON for the first time, it will deploy its config files, basic directory
structures, the example schema and will then ask whetever it shall create log files or not. If you intend on reporting bugs,
you might want to turn log file creation on. (A log will always be produced, but only written to the harddrive, when turning
this option on.) 

## UI elements

pyJSON features a graphical user interface in order to make table-like editing of JSON possible.

```{note}
pyJSON is in development and the interface might be subject to change.
```

```{image} Images/pyJSON_interface.png
:alt: The pyJSON interface, labeled with numbers. 
:width: 600px
```

1) **The menu bar** contains more advanced functions, such as storing and retrieving default templates for the current schema,
    reloading the current file and dropping changes or, in later stages, additional preferences.
2) **The schema and directory selector** lets the user choose the current schema or select one of the indexed directories for search.
    It also displays the last JSON document opened or created.
3) **The first group of buttons** contains buttons for adding a copy of a schema to the tools own storage, using the currently
    selected schema and entered information for a search in the currently selected indexed directory and adding a new directory
    for indexing.
4) **The second group of buttons** contains buttons for creating a blank JSON based on the current schema, open a JSON and save the
    currently entered information as a JSON document.
5) **The editing widget** is presenting the JSON document and its corresponding schema in a tabular fashion. It consists of 
    five columns.
   * The *Schema Key* column shows the nested structure as it is stored in the JSON (and the schema, if the JSON
       was created by pyJSON)
   * The *Title* shows a proper title. Note it will show either "KeyError" or "Type Error" if the Schema does not fit the
       JSON document properly.
   * The *Value* column is the only editable column by default. Enter values here. Input gets validated, when entered and will be
        rejected, if violating restrictions implied by the schema. The input form adapts to certain keywords.
   * The *Type* indicates, what type of data has to be entered.
   * The *Description* contains the content of the description stored in the schema.

## Notes and comments on behaviour
```{warning}
Saving a before opened then edited document will overwrite the original *without* further question!
```

## Tutorials

### Creating a JSON on a schema basis.
A core functionality of the pyJSON Schema Loader and Editor is the creation of a JSON document based on
a corresponding [JSON Schema](https://json-schema.org/), validating inputs and structure in the process.
In order to do so, one needs a JSON schema.

If pyJSON is not installed yet, please refer to the [installation](installation) pat of this document.
We create a JSON based on the integrated demo schema that gets deployed when first starting pyJSON.

1) Start pyJSON.
    * If not the case, select the "default.json" in the "Current Schema" drop down menu. Then, if needed, use the "New from 
        Schema" Button (see image above, first button of segment 4)
2) Enter some information. You _can_ leave entries blank, however keep in mind that your JSON might not validate against the
    schema, if the field must not be empty.
3) Click on the "Save" button. A dialog will appear in which you can select the location the file shall be saved in. A name,
    `_meta.json`, will be proposed. Navigate to a directory of your choice, change the name, if you want to and save the file.
4) You can check the file with an editor of your choice.

