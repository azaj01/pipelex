from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.core.concepts.concept_native import NativeConceptCode
from pipelex.core.stuffs.list_content import ListContent
from pipelex.core.stuffs.structured_content import StructuredContent
from pipelex.core.stuffs.stuff import Stuff
from pipelex.core.stuffs.text_content import TextContent


class MySubClass(StructuredContent):
    arg4: str


class MyConcept(StructuredContent):
    arg1: str
    arg2: int
    arg3: MySubClass


####################################################################################################
## CASE 1: I have directly the content.
# Possible solutions:
# 1.1: stuff_data is a string.
# 1.2: stuff_data is a list of strings.
# 1.3: stuff_data is a StuffContent object.
#      1.3a: Regular StuffContent object
#      1.3b: ListContent of StuffContent objects (special subcase)
# 1.4: stuff_data is a list of StuffContent objects.
####################################################################################################

# 1.1: Content is a string.
stuff_data11 = "my text"

# Stuff should be
stuff11 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
    content=TextContent(text="my_text"),
)

# 1.2: Content is a list of strings
stuff_data12 = ["test1", "test2", "test3"]

# Concept string needs to be compatible strictly with the concept native.Text. Otherwise it should raise an error.

stuff12 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),
    content=ListContent(items=[TextContent(text="test1"), TextContent(text="test2"), TextContent(text="test3")]),
)

# 1.3: Content is a StuffContent object.
stuff_data13 = MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))

# It should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it should raise an error.
# If no concept is found, it should raise an error.

stuff13 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
)

# 1.4: content is a list of StuffContent objects.
stuff_data14 = [MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))]

# It should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it should raise an error.
# EVERY item of the list should be of the same type. Otherwise it should raise an error.
# If no concept is found, it should raise an error.

stuff14 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=ListContent(
        items=[MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))]
    ),
)

# 1.3b (formerly 1.5): content is a ListContent of StuffContent objects.
# This is a special subcase of 1.3 since ListContent is itself a StuffContent.
stuff_data13b: ListContent[MyConcept] = ListContent(
    items=[MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))]
)

# It should check that every item in the list is a subclass of StuffContent.
# If not, it should raise an error.
# If every item is of the same type, it should create a Stuff with the concept of the first item (not from ListContent itself).
# If every item is not of the same type, it should raise an error.
# If the ListContent is empty, it should raise an error.
# If no concept is found, it should raise an error. To find the concept, it should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it should raise an error.
# If the domain is specified or found, it should check that the structure corresponds with the given content.
# Otherwise it should raise an error.

stuff13b = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=ListContent(
        items=[MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))]
    ),
)

####################################################################################################
## CASE 2: Here, we HAVE the key "concept_string" AND the key "content".
# The value of the "content" key can Either be a:
# 2.1: a string.
# 2.2: a list of strings.
# 2.3: a StuffContent object.
# 2.4: a list of StuffContent objects.
# 2.5: a dict (corresponding to the concept right above).
# 2.6: a list of dict (corresponding to the concept right above).
####################################################################################################

# 2.1: Content is a string

stuff_data21 = {"concept": "concept_string", "content": "my text"}

# Here, the concept can either be Text, native.Text or any other concept. But if its any other concept,
# it should be stricly compatible with the concept native.Text.

stuff21 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),  # Or else
    content=TextContent(text="my text"),
)

# 2.2: Content is a list of strings
stuff_data22 = {"concept": "concept_string", "content": ["text1", "text2", "text3"]}

# Here, the concept can either be Text, native.Text or any other concept. But if its any other concept,
#  it should be stricly compatible with the concept native.Text.

stuff22 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make_native_concept(native_concept_code=NativeConceptCode.TEXT),  # Or else
    content=ListContent(items=[TextContent(text="text1"), TextContent(text="text2"), TextContent(text="text3")]),
)

# 2.3: Content is a StuffContent object
stuff_data23 = {"concept": "concept_string", "content": MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))}

# For the concept mentioned: If no domain is specified, it should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it should raise an error
# and ask the user to specify the domain.
# If the domain is specified or found, it should check that the structure corresponds with the given content.
# Otherwise it should raise an error.

stuff23 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
)

# 2.4: Content is a list of StuffContent objects
stuff_data24 = {
    "concept": "concept_string",
    "content": [MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))],
}

stuff24 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=ListContent(
        items=[MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")), MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))]
    ),
)

# 2.5: Content is a dict
stuff_data25 = {"concept": "concept_string", "content": {"arg1": "something", "arg2": 1, "arg3": {"arg4": "something else else"}}}

# For the concept mentioned: If no domain is specified, it should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it should raise an error
# and ask the user to specify the domain.
# If the domain is specified or found, it should check that the structure corresponds with the given content by validating the model.
# Otherwise it should raise an error.

stuff25 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=MyConcept(arg1="something", arg2=1, arg3=MySubClass(arg4="something else else")),
)

# 2.6: Content is a list of dict
stuff_data26 = {
    "concept": "concept_string",
    "content": [
        {"arg1": "something", "arg2": 1, "arg3": {"arg4": "something else else"}},
        {"arg1": "something else", "arg2": 2, "arg3": {"arg4": "something else else else"}},
    ],
}

# For the concept mentioned: If no domain is specified, it should look in all the library for the concept with the same name.
# If no search domains are provided and we find 2 or more concepts with the same name, it
# should raise an error and ask the user to specify the domain.
# If the domain is specified or found, it should check that the structure corresponds with the given content by validating the model.
# Otherwise it should raise an error.

stuff26 = Stuff(
    stuff_code="stuff_code",
    stuff_name="stuff_name",
    concept=ConceptFactory.make(concept_code="MyConcept", domain="domain", description="description", structure_class_name=MyConcept.__name__),
    content=ListContent(
        items=[
            MyConcept(arg1="something", arg2=1, arg3=MySubClass(arg4="something else else")),
            MyConcept(arg1="something else", arg2=2, arg3=MySubClass(arg4="something else else else")),
        ]
    ),
)
