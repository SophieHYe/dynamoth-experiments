#!/usr/bin/env python

import os
import re
import json
from core.Config import conf

def get_java_version_in_file(propertiesPath):
    target = None
    source = None         
    with open(propertiesPath) as file:
        for line in file:
            m = re.search('compile.target ?= ?1.([0-9])', line)
            if m:
                target = m.group(1)
            else:
                m = re.search('target>1.([0-9])', line)
                if m:
                    target = m.group(1)
                else:
                    m = re.search('target="1.([0-9])"', line)
                    if m:
                        target = m.group(1)
                    else:
                        m = re.search('name="ant.build.javac.target" value="1.([0-9])"', line)
                        if m:
                            target = m.group(1)

            m = re.search('compile.source ?= ?1.([0-9])', line)
            if m:
                source = m.group(1)
            else:
                m = re.search('source>1.([0-9])', line)
                if m:
                    source = m.group(1)
                else:
                    m = re.search('source="1.([0-9])"', line)
                    if m:
                        source = m.group(1)
                    else:
                        m = re.search('name="ant.build.javac.source" value="1.([0-9])"', line)
                        if m:
                            source = m.group(1)
    return (source, target)

rootProjects = conf.projectsRoot
rootProjectsData = os.path.join(conf.defects4jRepairRoot, "src", "python", "data", "projects")
for project in sorted(os.listdir(rootProjects)):
    projectPath = os.path.join(rootProjects, project)
    projectDataPath = os.path.join(rootProjectsData, project.lower() + ".json")
    print(project)
    if not os.path.exists(projectDataPath):
        continue
    if os.path.isfile(projectPath):
        continue
    data_file = open(projectDataPath, "r+")
    data = json.load(data_file)
    if "complianceLevel" not in data:
        data["complianceLevel"] = {}
    for bugId in sorted(os.listdir(projectPath)):
        bugPath = os.path.join(projectPath, bugId)
        if os.path.isfile(bugPath):
            continue
        files = ["pom.xml", "project.properties", "default.properties", "ant/build.xml", "build.xml"]
        target = None
        source = None
        for file in files:
            propertiesPath = os.path.join(bugPath, file)
            if os.path.exists(propertiesPath):
                (source, target) = get_java_version_in_file(propertiesPath)
                if (target is not None):
                    break
        if target is None:
            target = "7"
            source = "7"
        data["complianceLevel"][bugId.split("_")[1]] = {
            "target": int(target),
            "source": int(source)
        }
    data_file.seek(0)
    data_file.write(json.dumps(data, indent=4, sort_keys=True))
    data_file.truncate()
    data_file.close()
