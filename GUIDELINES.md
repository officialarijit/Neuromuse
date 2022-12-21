# Guidelines

This repository contains a template *README* to document a repository for a new open source project.	
See at <https://www.eurecat.org/docs/releasing> for more information about releasing new Eurecat open source projects.

## Pusblishing Steps

1. Write a note to describe briefly your code, including:   
    - Title of the project.  
    - Brief description of the code's purpose.  
    - Code access link (private for the moment).    
    - Any additional consideration that you consider relevant for the publishing review.    
2. Use the note to ask your unit director and scientific director whether the code is susceptible for open source publishing. Note that if the code is a modification of an existing code licensed as GPL or CC NC-ND-SA, or if it is simply a snippet, then it could be directly referred to the step 4.    	
3. Otherwise, the code has to apply for publishing to the Open Source Eurecat committee.  
4. Any publication needs to request access to the account administrator(s) at <https://github.com/eurecat>. Afterwards the pushes to that repository are freely granted for the developer. For repositories already existent, access request is also a requisite. 	
5. Further versions of the code affecting any publishing aspect considered throughout the above steps must be re-submitted for review from the step 1.   

## How to Use this Template

1. Check it out from GitHub (no need to fork it).
2. Copy these files to your repository folder, except this file *GUIDELINES*.
3. Populate the copied *README* file with the correspoding info.
4. Modify the *CONTRIBUTING* file according to the project requirements.
5. Keep on coding! and documenting!


## General Guidelines

- Use **ENGLISH** as unique language for coding and documenting.
- Document often the code, the README file and additional info files.
- [Markdown](https://guides.github.com/features/mastering-markdown) flavor makes receipts tasty.


## Coding Style

Currently there are no programming style guidelines regarding variable naming, indentatins, vertical aligment,... etc.	
In general follow the style already formatting the project and do your best.	
May be interesting to have a look to [programming style](https://en.wikipedia.org/wiki/Programming_style) or [naming convention](https://en.wikipedia.org/wiki/Naming_convention_\(programming\)).


# Project Screening

Remove names, email address, IP addresses and in general sensible information including internal paths or filenames, unless explicit permission for that.

You may find useful screening commands like:

```shell
egrep -r '\.eurecat\.com|@eurecat\.com|eurecat?/|([0-9]+\.){3}[0-9]+' <path-to-source-directory>
```


## Source Code Headers

EVERY file containing source code must include copyright and license information.

Apache header:

    Copyright 2018 Eurecat

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

MIT and Apache 2.0 licenses will be favoured.	
See the documentation for instructions on using alternate license.	
You may find useful this [autogen](https://github.com/mbrukman/autogen) tool to generate license headers including some sample outputs. 


-----------------------

Copyright 2018 Eurecat