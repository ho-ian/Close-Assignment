# Close-Assignment

A. Explains your script’s logic to someone that is not overly technical. How did you eliminate the
invalid data? How did you find all the leads? How did you segment the leads by state and find
the one with the most revenue?

In this repository, you will find two files: sample_script.py and close.py. The main file we're working with is
the sample_script.py file where the assignment is broken down into Part A, B, and C. I initially load the csv data
into Pandas dataframes on Python and then in Part A, I break down importing the data into Close into three parts.
The first part, we upload/post all the unique leads in the data set. In Close, this generates a unique lead id for
each Company, we then grab all the lead ids by using a GET lead API call. Then we import the Contacts making sure
to match them up to the correct Company. 

In the data set, there were some invalid data points. In the Contact Name column, any empty data entries were marked
with "No Name" when imported to Close. For any invalid emails, we eliminated any emails that did not have the format 
of abcde@xyz.qwe. As for phone numbers, I removed any phone numbers that included alphabetical letters and also numbers
shorter than 7 digits. For the purposes of this sample data set, it worked sufficiently but missed one edge case. In the 
future if I have more time, I would rewrite the phone number validation logic to eliminate more edge cases.

After importing the csv file into Pandas Dataframes, I found all the leads by eliminating any duplicate rows.
This should find all the unique leads because any Company that may have the same name but is from a differnt State,
has a different Revenue, or is founded on a different date could be considered a completely new lead.

I was able to segment leads by state using a method called group_by as part of the Pandas Dataframes package.
The logic is to group the dataframe by their respective states and then calculating each state's max revenue
while including the lead it came from.

B. Explains how to run the script, including any dependencies that must be downloaded for the
script to run.

## Dependencies
`pip install closeio`
`pip install pandas`

The script is meant to be run on a terminal like bash and is meant to include two additional arguments for part B.
The two additional arguments is for specifying the date range we want to find leads founded within and the format 
is currently set to '%d.%m.%Y' only.

Example:
``python sample_script.py 12.12.1980 1.5.2008``

Example Output:
``0       Digitube
15         Yombu
19         Oyope
23          Geba
28         Ainyx
37          Vitz
38    Zoomlounge
42       Cogibox
49     Skynoodle
53       Gabvine
54       Tagopia
70         Voomm
75        Avavee
78      Flashset
80       Voolith
91          Fatz
93        Eimbee``


