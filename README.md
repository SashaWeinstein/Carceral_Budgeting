# Suffolk County Carceral Spending Analysis

Project for fellowship with Suffolk County District Attorney's office

Full methodology is in methodology.pdf

Analysis starts with Initialize_Agencies.py which creates agency objects. Measures of total spending across various cost types and agencies are compiled by iterating through agency objects.

## Agency Inheritence Tree

Each of the 14 agencies is represented as a subclass off an inheritance tree with the Agency class as the top parent. Agency subclasses into StateAgency and PoliceDepartment. The state agencies with no special modifications to their methodology are represented as StateAgency classes and several state agencies subclass off StateAgency. All police departments are represented as subclasses off the PoliceDepartment class

## Agency Costs
Costs are stored as attributes of each agency. Each agency has the cost types of non-payroll operating, payroll, pensions costs, fringe benefit costs, and pension costs. Some of these costs are comprised of a *stated* and *hidden* portion. Stated costs are listed in the expenditure record for an agency and hidden costs are listed outside the expenditure record. A full description is available in the methodology pdf.

Code to generate agency costs is split across the agency classes and code in the Cost_Type_Code directory.

## Agency correction
Some agencies operate across the entire state of Massachussetts and so only the fraction of their expenditures spent in Suffolk county are counted. Code to calculate these correctons is in Agency_Corrections, agencies are assigned a correction on initialization.

## Final Results
Final results are generated with ipython notebook that loops through all agency classes. 


## Other Directories
 - Check implementation has code to double check results
 - Exploratory has code used in early planning stages, mostly jupyter notebooks
 - Misc Analyses has code used for questions that came up during analysis not directly related to final result of carceral budgets
 - Presentations has code used to develop presentations
 - Visualize includes code to make various plots
