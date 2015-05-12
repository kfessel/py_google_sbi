#py_google_sbi

py_google_sbi is a Python Google search by image (sbi) interface. It contains a standalone version or may be used as a Python module.

The web-page-results are parsed using regular expressions which makes the module sensitive to changes on Google servers since no API is used.

#How does it work

It uploads the picture to Google sbi, searches the result for Tags which would be used for a Google search regarding the Image and searches the similar Image Pages parsing their Descriptions for words and bigrams counting them and returning the most common.

Google accepts many image formats (e.g. png jpeg bmp gif webm) for incompatible formats the module just gives no results (no error to try fetch).

