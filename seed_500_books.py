"""
Seed Data Script - 500 Popular Books, Members, and Loans
========================================================
Populates library.db with 500 well-known popular books across diverse genres,
along with sample members and active/overdue loans to immediately demonstrate
the upgraded library system's analytics, fines, and borrowing workflows.
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")

# ----------------------------------------------------------------------
# 500 Popular Real Books Curated by Genre
# ----------------------------------------------------------------------
CURATED_BOOKS = [
    # --- Classic Literature (90 books) ---
    ("To Kill a Mockingbird", "Harper Lee", "9780061120084", "Classics", "Shelf A-01"),
    ("1984", "George Orwell", "9780451524935", "Classics", "Shelf A-02"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Classics", "Shelf A-03"),
    ("Pride and Prejudice", "Jane Austen", "9780141439518", "Classics", "Shelf A-04"),
    ("The Catcher in the Rye", "J.D. Salinger", "9780316769488", "Classics", "Shelf A-05"),
    ("Jane Eyre", "Charlotte Bronte", "9780141441146", "Classics", "Shelf A-06"),
    ("Wuthering Heights", "Emily Bronte", "9780141439556", "Classics", "Shelf A-07"),
    ("Crime and Punishment", "Fyodor Dostoevsky", "9780140449136", "Classics", "Shelf A-08"),
    ("The Brothers Karamazov", "Fyodor Dostoevsky", "9780374528379", "Classics", "Shelf A-09"),
    ("War and Peace", "Leo Tolstoy", "9781400079988", "Classics", "Shelf A-10"),
    ("Anna Karenina", "Leo Tolstoy", "9780143035008", "Classics", "Shelf A-11"),
    ("Moby-Dick", "Herman Melville", "9781503280786", "Classics", "Shelf A-12"),
    ("The Odyssey", "Homer", "9780140268867", "Classics", "Shelf A-13"),
    ("The Iliad", "Homer", "9780140275360", "Classics", "Shelf A-14"),
    ("Great Expectations", "Charles Dickens", "9780141439563", "Classics", "Shelf A-15"),
    ("A Tale of Two Cities", "Charles Dickens", "9780141439600", "Classics", "Shelf A-16"),
    ("Oliver Twist", "Charles Dickens", "9780141439747", "Classics", "Shelf A-17"),
    ("The Picture of Dorian Gray", "Oscar Wilde", "9780141439570", "Classics", "Shelf A-18"),
    ("Frankenstein", "Mary Shelley", "9780141439471", "Classics", "Shelf A-19"),
    ("Dracula", "Bram Stoker", "9780141439846", "Classics", "Shelf A-20"),
    ("The Count of Monte Cristo", "Alexandre Dumas", "9780140449266", "Classics", "Shelf A-21"),
    ("The Three Musketeers", "Alexandre Dumas", "9780140440256", "Classics", "Shelf A-22"),
    ("Les Miserables", "Victor Hugo", "9780451419439", "Classics", "Shelf A-23"),
    ("The Hunchback of Notre-Dame", "Victor Hugo", "9780140443530", "Classics", "Shelf A-24"),
    ("Brave New World", "Aldous Huxley", "9780060850524", "Classics", "Shelf A-25"),
    ("Animal Farm", "George Orwell", "9780451526342", "Classics", "Shelf A-26"),
    ("Fahrenheit 451", "Ray Bradbury", "9781451673319", "Classics", "Shelf A-27"),
    ("Lord of the Flies", "William Golding", "9780399501487", "Classics", "Shelf A-28"),
    ("The Old Man and the Sea", "Ernest Hemingway", "9780684801223", "Classics", "Shelf A-29"),
    ("For Whom the Bell Tolls", "Ernest Hemingway", "9780684803357", "Classics", "Shelf A-30"),
    ("A Farewell to Arms", "Ernest Hemingway", "9780684801469", "Classics", "Shelf A-31"),
    ("The Sun Also Rises", "Ernest Hemingway", "9780743297332", "Classics", "Shelf A-32"),
    ("The Grapes of Wrath", "John Steinbeck", "9780143039433", "Classics", "Shelf A-33"),
    ("East of Eden", "John Steinbeck", "9780140186390", "Classics", "Shelf A-34"),
    ("Of Mice and Men", "John Steinbeck", "9780140177398", "Classics", "Shelf A-35"),
    ("Slaughterhouse-Five", "Kurt Vonnegut", "9780385333849", "Classics", "Shelf A-36"),
    ("Cat's Cradle", "Kurt Vonnegut", "9780385333481", "Classics", "Shelf A-37"),
    ("Catch-22", "Joseph Heller", "9781451626650", "Classics", "Shelf A-38"),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "9780060883287", "Classics", "Shelf A-39"),
    ("Love in the Time of Cholera", "Gabriel Garcia Marquez", "9780307389732", "Classics", "Shelf A-40"),
    ("The Metamorphosis", "Franz Kafka", "9780553213690", "Classics", "Shelf A-41"),
    ("The Trial", "Franz Kafka", "9780805209990", "Classics", "Shelf A-42"),
    ("The Stranger", "Albert Camus", "9780679720201", "Classics", "Shelf A-43"),
    ("The Plague", "Albert Camus", "9780679720218", "Classics", "Shelf A-44"),
    ("The Myth of Sisyphus", "Albert Camus", "9780679733737", "Classics", "Shelf A-45"),
    ("Heart of Darkness", "Joseph Conrad", "9780141441672", "Classics", "Shelf A-46"),
    ("Lord Jim", "Joseph Conrad", "9780141441221", "Classics", "Shelf A-47"),
    ("The Secret Agent", "Joseph Conrad", "9780141441580", "Classics", "Shelf A-48"),
    ("Madame Bovary", "Gustave Flaubert", "9780140449129", "Classics", "Shelf A-49"),
    ("Don Quixote", "Miguel de Cervantes", "9780060934347", "Classics", "Shelf A-50"),
    ("Ulysses", "James Joyce", "9780199535675", "Classics", "Shelf A-51"),
    ("A Portrait of the Artist as a Young Man", "James Joyce", "9780142437346", "Classics", "Shelf A-52"),
    ("Dubliners", "James Joyce", "9780140247749", "Classics", "Shelf A-53"),
    ("To the Lighthouse", "Virginia Woolf", "9780156907392", "Classics", "Shelf A-54"),
    ("Mrs Dalloway", "Virginia Woolf", "9780156628709", "Classics", "Shelf A-55"),
    ("Orlando", "Virginia Woolf", "9780156701600", "Classics", "Shelf A-56"),
    ("A Room of One's Own", "Virginia Woolf", "9780156030410", "Classics", "Shelf A-57"),
    ("The Sound and the Fury", "William Faulkner", "9780679732242", "Classics", "Shelf A-58"),
    ("As I Lay Dying", "William Faulkner", "9780679732259", "Classics", "Shelf A-59"),
    ("Light in August", "William Faulkner", "9780679732266", "Classics", "Shelf A-60"),
    ("Invisible Man", "Ralph Ellison", "9780679732761", "Classics", "Shelf A-61"),
    ("Beloved", "Toni Morrison", "9781400033416", "Classics", "Shelf A-62"),
    ("Song of Solomon", "Toni Morrison", "9781400033423", "Classics", "Shelf A-63"),
    ("The Bluest Eye", "Toni Morrison", "9780452282193", "Classics", "Shelf A-64"),
    ("Things Fall Apart", "Chinua Achebe", "9780385474542", "Classics", "Shelf A-65"),
    ("No Longer at Ease", "Chinua Achebe", "9780385474559", "Classics", "Shelf A-66"),
    ("Midnight's Children", "Salman Rushdie", "9780812976533", "Classics", "Shelf A-67"),
    ("The Satanic Verses", "Salman Rushdie", "9780812976717", "Classics", "Shelf A-68"),
    ("The Master and Margarita", "Mikhail Bulgakov", "9780141180144", "Classics", "Shelf A-69"),
    ("Fathers and Sons", "Ivan Turgenev", "9780140449211", "Classics", "Shelf A-70"),
    ("Dead Souls", "Nikolai Gogol", "9780140448078", "Classics", "Shelf A-71"),
    ("The Death of Ivan Ilyich", "Leo Tolstoy", "9780307388865", "Classics", "Shelf A-72"),
    ("Notes from Underground", "Fyodor Dostoevsky", "9780679734529", "Classics", "Shelf A-73"),
    ("The Idiot", "Fyodor Dostoevsky", "9780375702242", "Classics", "Shelf A-74"),
    ("Demons", "Fyodor Dostoevsky", "9780679734512", "Classics", "Shelf A-75"),
    ("David Copperfield", "Charles Dickens", "9780140439441", "Classics", "Shelf A-76"),
    ("Bleak House", "Charles Dickens", "9780141439723", "Classics", "Shelf A-77"),
    ("Hard Times", "Charles Dickens", "9780141439679", "Classics", "Shelf A-78"),
    ("Sense and Sensibility", "Jane Austen", "9780141439662", "Classics", "Shelf A-79"),
    ("Emma", "Jane Austen", "9780141439587", "Classics", "Shelf A-80"),
    ("Mansfield Park", "Jane Austen", "9780141439808", "Classics", "Shelf A-81"),
    ("Northanger Abbey", "Jane Austen", "9780141439792", "Classics", "Shelf A-82"),
    ("Persuasion", "Jane Austen", "9780141439686", "Classics", "Shelf A-83"),
    ("The Canterbury Tales", "Geoffrey Chaucer", "9780140424386", "Classics", "Shelf A-84"),
    ("The Divine Comedy", "Dante Alighieri", "9780142437223", "Classics", "Shelf A-85"),
    ("Paradise Lost", "John Milton", "9780140424393", "Classics", "Shelf A-86"),
    ("Hamlet", "William Shakespeare", "9780743477123", "Classics", "Shelf A-87"),
    ("Macbeth", "William Shakespeare", "9780743477109", "Classics", "Shelf A-88"),
    ("Othello", "William Shakespeare", "9780743477550", "Classics", "Shelf A-89"),
    ("Romeo and Juliet", "William Shakespeare", "9780743477116", "Classics", "Shelf A-90"),

    # --- Science Fiction & Fantasy (110 books) ---
    ("The Hobbit", "J.R.R. Tolkien", "9780547928227", "Sci-Fi & Fantasy", "Shelf B-01"),
    ("The Fellowship of the Ring", "J.R.R. Tolkien", "9780547928210", "Sci-Fi & Fantasy", "Shelf B-02"),
    ("The Two Towers", "J.R.R. Tolkien", "9780547928203", "Sci-Fi & Fantasy", "Shelf B-03"),
    ("The Return of the King", "J.R.R. Tolkien", "9780547928197", "Sci-Fi & Fantasy", "Shelf B-04"),
    ("The Silmarillion", "J.R.R. Tolkien", "9780544338012", "Sci-Fi & Fantasy", "Shelf B-05"),
    ("Dune", "Frank Herbert", "9780441172719", "Sci-Fi & Fantasy", "Shelf B-06"),
    ("Dune Messiah", "Frank Herbert", "9780441172696", "Sci-Fi & Fantasy", "Shelf B-07"),
    ("Children of Dune", "Frank Herbert", "9780441104024", "Sci-Fi & Fantasy", "Shelf B-08"),
    ("God Emperor of Dune", "Frank Herbert", "9780441294671", "Sci-Fi & Fantasy", "Shelf B-09"),
    ("Heretics of Dune", "Frank Herbert", "9780441328000", "Sci-Fi & Fantasy", "Shelf B-10"),
    ("Chapterhouse: Dune", "Frank Herbert", "9780441102679", "Sci-Fi & Fantasy", "Shelf B-11"),
    ("Foundation", "Isaac Asimov", "9780553293357", "Sci-Fi & Fantasy", "Shelf B-12"),
    ("Foundation and Empire", "Isaac Asimov", "9780553293371", "Sci-Fi & Fantasy", "Shelf B-13"),
    ("Second Foundation", "Isaac Asimov", "9780553293364", "Sci-Fi & Fantasy", "Shelf B-14"),
    ("I, Robot", "Isaac Asimov", "9780553382563", "Sci-Fi & Fantasy", "Shelf B-15"),
    ("The Caves of Steel", "Isaac Asimov", "9780553288285", "Sci-Fi & Fantasy", "Shelf B-16"),
    ("Neuromancer", "William Gibson", "9780441569595", "Sci-Fi & Fantasy", "Shelf B-17"),
    ("Count Zero", "William Gibson", "9780441013678", "Sci-Fi & Fantasy", "Shelf B-18"),
    ("Mona Lisa Overdrive", "William Gibson", "9780553281743", "Sci-Fi & Fantasy", "Shelf B-19"),
    ("Snow Crash", "Neal Stephenson", "9780553380958", "Sci-Fi & Fantasy", "Shelf B-20"),
    ("The Diamond Age", "Neal Stephenson", "9780553380965", "Sci-Fi & Fantasy", "Shelf B-21"),
    ("Cryptonomicon", "Neal Stephenson", "9780060512804", "Sci-Fi & Fantasy", "Shelf B-22"),
    ("Anathem", "Neal Stephenson", "9780061474101", "Sci-Fi & Fantasy", "Shelf B-23"),
    ("2001: A Space Odyssey", "Arthur C. Clarke", "9780451457998", "Sci-Fi & Fantasy", "Shelf B-24"),
    ("Rendezvous with Rama", "Arthur C. Clarke", "9780553287899", "Sci-Fi & Fantasy", "Shelf B-25"),
    ("Childhood's End", "Arthur C. Clarke", "9780345347954", "Sci-Fi & Fantasy", "Shelf B-26"),
    ("Do Androids Dream of Electric Sheep?", "Philip K. Dick", "9780345404473", "Sci-Fi & Fantasy", "Shelf B-27"),
    ("The Man in the High Castle", "Philip K. Dick", "9780547572482", "Sci-Fi & Fantasy", "Shelf B-28"),
    ("Ubik", "Philip K. Dick", "9780547572291", "Sci-Fi & Fantasy", "Shelf B-29"),
    ("A Scanner Darkly", "Philip K. Dick", "9780547572178", "Sci-Fi & Fantasy", "Shelf B-30"),
    ("The Left Hand of Darkness", "Ursula K. Le Guin", "9780441478125", "Sci-Fi & Fantasy", "Shelf B-31"),
    ("The Dispossessed", "Ursula K. Le Guin", "9780060512750", "Sci-Fi & Fantasy", "Shelf B-32"),
    ("A Wizard of Earthsea", "Ursula K. Le Guin", "9780547773742", "Sci-Fi & Fantasy", "Shelf B-33"),
    ("The Tombs of Atuan", "Ursula K. Le Guin", "9780547773735", "Sci-Fi & Fantasy", "Shelf B-34"),
    ("The Farthest Shore", "Ursula K. Le Guin", "9780547773704", "Sci-Fi & Fantasy", "Shelf B-35"),
    ("Hyperion", "Dan Simmons", "9780553283686", "Sci-Fi & Fantasy", "Shelf B-36"),
    ("The Fall of Hyperion", "Dan Simmons", "9780553288209", "Sci-Fi & Fantasy", "Shelf B-37"),
    ("Endymion", "Dan Simmons", "9780553572940", "Sci-Fi & Fantasy", "Shelf B-38"),
    ("The Rise of Endymion", "Dan Simmons", "9780553572988", "Sci-Fi & Fantasy", "Shelf B-39"),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "9780345391803", "Sci-Fi & Fantasy", "Shelf B-40"),
    ("The Restaurant at the End of the Universe", "Douglas Adams", "9780345391810", "Sci-Fi & Fantasy", "Shelf B-41"),
    ("Life, the Universe and Everything", "Douglas Adams", "9780345391827", "Sci-Fi & Fantasy", "Shelf B-42"),
    ("Ender's Game", "Orson Scott Card", "9780812550702", "Sci-Fi & Fantasy", "Shelf B-43"),
    ("Speaker for the Dead", "Orson Scott Card", "9780812550757", "Sci-Fi & Fantasy", "Shelf B-44"),
    ("Xenocide", "Orson Scott Card", "9780812509250", "Sci-Fi & Fantasy", "Shelf B-45"),
    ("The Name of the Wind", "Patrick Rothfuss", "9780756404741", "Sci-Fi & Fantasy", "Shelf B-46"),
    ("The Wise Man's Fear", "Patrick Rothfuss", "9780756407919", "Sci-Fi & Fantasy", "Shelf B-47"),
    ("The Way of Kings", "Brandon Sanderson", "9780765365279", "Sci-Fi & Fantasy", "Shelf B-48"),
    ("Words of Radiance", "Brandon Sanderson", "9780765365286", "Sci-Fi & Fantasy", "Shelf B-49"),
    ("Oathbringer", "Brandon Sanderson", "9780765365293", "Sci-Fi & Fantasy", "Shelf B-50"),
    ("Rhythm of War", "Brandon Sanderson", "9780765326386", "Sci-Fi & Fantasy", "Shelf B-51"),
    ("Mistborn: The Final Empire", "Brandon Sanderson", "9780765350381", "Sci-Fi & Fantasy", "Shelf B-52"),
    ("The Well of Ascension", "Brandon Sanderson", "9780765351425", "Sci-Fi & Fantasy", "Shelf B-53"),
    ("The Hero of Ages", "Brandon Sanderson", "9780765356130", "Sci-Fi & Fantasy", "Shelf B-54"),
    ("Elantris", "Brandon Sanderson", "9780765350374", "Sci-Fi & Fantasy", "Shelf B-55"),
    ("Warbreaker", "Brandon Sanderson", "9780765360038", "Sci-Fi & Fantasy", "Shelf B-56"),
    ("A Game of Thrones", "George R.R. Martin", "9780553593716", "Sci-Fi & Fantasy", "Shelf B-57"),
    ("A Clash of Kings", "George R.R. Martin", "9780553579901", "Sci-Fi & Fantasy", "Shelf B-58"),
    ("A Storm of Swords", "George R.R. Martin", "9780553573428", "Sci-Fi & Fantasy", "Shelf B-59"),
    ("A Feast for Crows", "George R.R. Martin", "9780553582024", "Sci-Fi & Fantasy", "Shelf B-60"),
    ("A Dance with Dragons", "George R.R. Martin", "9780553582017", "Sci-Fi & Fantasy", "Shelf B-61"),
    ("The Eye of the World", "Robert Jordan", "9780812511819", "Sci-Fi & Fantasy", "Shelf B-62"),
    ("The Great Hunt", "Robert Jordan", "9780812517729", "Sci-Fi & Fantasy", "Shelf B-63"),
    ("The Dragon Reborn", "Robert Jordan", "9780812513714", "Sci-Fi & Fantasy", "Shelf B-64"),
    ("The Shadow Rising", "Robert Jordan", "9780812513738", "Sci-Fi & Fantasy", "Shelf B-65"),
    ("The Fires of Heaven", "Robert Jordan", "9780812550306", "Sci-Fi & Fantasy", "Shelf B-66"),
    ("Good Omens", "Neil Gaiman & Terry Pratchett", "9780060853983", "Sci-Fi & Fantasy", "Shelf B-67"),
    ("American Gods", "Neil Gaiman", "9780062564252", "Sci-Fi & Fantasy", "Shelf B-68"),
    ("Coraline", "Neil Gaiman", "9780380807345", "Sci-Fi & Fantasy", "Shelf B-69"),
    ("The Graveyard Book", "Neil Gaiman", "9780060530945", "Sci-Fi & Fantasy", "Shelf B-70"),
    ("Neverwhere", "Neil Gaiman", "9780060557812", "Sci-Fi & Fantasy", "Shelf B-71"),
    ("Stardust", "Neil Gaiman", "9780061147258", "Sci-Fi & Fantasy", "Shelf B-72"),
    ("The Colour of Magic", "Terry Pratchett", "9780062225672", "Sci-Fi & Fantasy", "Shelf B-73"),
    ("The Light Fantastic", "Terry Pratchett", "9780062225689", "Sci-Fi & Fantasy", "Shelf B-74"),
    ("Mort", "Terry Pratchett", "9780062225719", "Sci-Fi & Fantasy", "Shelf B-75"),
    ("Guards! Guards!", "Terry Pratchett", "9780062225757", "Sci-Fi & Fantasy", "Shelf B-76"),
    ("Small Gods", "Terry Pratchett", "9780062237378", "Sci-Fi & Fantasy", "Shelf B-77"),
    ("Going Postal", "Terry Pratchett", "9780060013172", "Sci-Fi & Fantasy", "Shelf B-78"),
    ("Leviathan Wakes", "James S.A. Corey", "9780316129084", "Sci-Fi & Fantasy", "Shelf B-79"),
    ("Caliban's War", "James S.A. Corey", "9780316129060", "Sci-Fi & Fantasy", "Shelf B-80"),
    ("Abaddon's Gate", "James S.A. Corey", "9780316129077", "Sci-Fi & Fantasy", "Shelf B-81"),
    ("Cibola Burn", "James S.A. Corey", "9780316217620", "Sci-Fi & Fantasy", "Shelf B-82"),
    ("Nemesis Games", "James S.A. Corey", "9780316334716", "Sci-Fi & Fantasy", "Shelf B-83"),
    ("Babylon's Ashes", "James S.A. Corey", "9780316334747", "Sci-Fi & Fantasy", "Shelf B-84"),
    ("Persepolis Rising", "James S.A. Corey", "9780316332835", "Sci-Fi & Fantasy", "Shelf B-85"),
    ("Tiamat's Wrath", "James S.A. Corey", "9780316332866", "Sci-Fi & Fantasy", "Shelf B-86"),
    ("The Three-Body Problem", "Cixin Liu", "9780765382030", "Sci-Fi & Fantasy", "Shelf B-87"),
    ("The Dark Forest", "Cixin Liu", "9780765386694", "Sci-Fi & Fantasy", "Shelf B-88"),
    ("Death's End", "Cixin Liu", "9780765377104", "Sci-Fi & Fantasy", "Shelf B-89"),
    ("The Martian", "Andy Weir", "9780553418026", "Sci-Fi & Fantasy", "Shelf B-90"),
    ("Project Hail Mary", "Andy Weir", "9780593135204", "Sci-Fi & Fantasy", "Shelf B-91"),
    ("Artemis", "Andy Weir", "9780553448122", "Sci-Fi & Fantasy", "Shelf B-92"),
    ("Red Rising", "Pierce Brown", "9780345539809", "Sci-Fi & Fantasy", "Shelf B-93"),
    ("Golden Son", "Pierce Brown", "9780345539823", "Sci-Fi & Fantasy", "Shelf B-94"),
    ("Morning Star", "Pierce Brown", "9780345539847", "Sci-Fi & Fantasy", "Shelf B-95"),
    ("Iron Gold", "Pierce Brown", "9780425285916", "Sci-Fi & Fantasy", "Shelf B-96"),
    ("Dark Age", "Pierce Brown", "9780425285947", "Sci-Fi & Fantasy", "Shelf B-97"),
    ("Old Man's War", "John Scalzi", "9780765348272", "Sci-Fi & Fantasy", "Shelf B-98"),
    ("The Ghost Brigades", "John Scalzi", "9780765354068", "Sci-Fi & Fantasy", "Shelf B-99"),
    ("The Last Colony", "John Scalzi", "9780765356185", "Sci-Fi & Fantasy", "Shelf B-100"),
    ("Redshirts", "John Scalzi", "9780765334794", "Sci-Fi & Fantasy", "Shelf B-101"),
    ("The Kaiju Preservation Society", "John Scalzi", "9780765389121", "Sci-Fi & Fantasy", "Shelf B-102"),
    ("Ancillary Justice", "Ann Leckie", "9780316246620", "Sci-Fi & Fantasy", "Shelf B-103"),
    ("Ancillary Sword", "Ann Leckie", "9780316246651", "Sci-Fi & Fantasy", "Shelf B-104"),
    ("Ancillary Mercy", "Ann Leckie", "9780316246682", "Sci-Fi & Fantasy", "Shelf B-105"),
    ("Children of Time", "Adrian Tchaikovsky", "9780316452502", "Sci-Fi & Fantasy", "Shelf B-106"),
    ("Children of Ruin", "Adrian Tchaikovsky", "9780316452533", "Sci-Fi & Fantasy", "Shelf B-107"),
    ("Blindsight", "Peter Watts", "9780765319647", "Sci-Fi & Fantasy", "Shelf B-108"),
    ("Altered Carbon", "Richard K. Morgan", "9780345457684", "Sci-Fi & Fantasy", "Shelf B-109"),
    ("A Fire Upon the Deep", "Vernor Vinge", "9780812528732", "Sci-Fi & Fantasy", "Shelf B-110"),

    # --- Mystery, Thriller & Crime (80 books) ---
    ("The Hound of the Baskervilles", "Arthur Conan Doyle", "9780141439693", "Mystery & Thriller", "Shelf C-01"),
    ("A Study in Scarlet", "Arthur Conan Doyle", "9780141441368", "Mystery & Thriller", "Shelf C-02"),
    ("The Sign of the Four", "Arthur Conan Doyle", "9780141441375", "Mystery & Thriller", "Shelf C-03"),
    ("The Adventures of Sherlock Holmes", "Arthur Conan Doyle", "9780141034324", "Mystery & Thriller", "Shelf C-04"),
    ("And Then There Were None", "Agatha Christie", "9780062073488", "Mystery & Thriller", "Shelf C-05"),
    ("Murder on the Orient Express", "Agatha Christie", "9780062073495", "Mystery & Thriller", "Shelf C-06"),
    ("The Murder of Roger Ackroyd", "Agatha Christie", "9780062073563", "Mystery & Thriller", "Shelf C-07"),
    ("Death on the Nile", "Agatha Christie", "9780062073556", "Mystery & Thriller", "Shelf C-08"),
    ("The ABC Murders", "Agatha Christie", "9780062073587", "Mystery & Thriller", "Shelf C-09"),
    ("The Da Vinci Code", "Dan Brown", "9780307474278", "Mystery & Thriller", "Shelf C-10"),
    ("Angels & Demons", "Dan Brown", "9781416524793", "Mystery & Thriller", "Shelf C-11"),
    ("Inferno", "Dan Brown", "9780307950680", "Mystery & Thriller", "Shelf C-12"),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "9780307949486", "Mystery & Thriller", "Shelf C-13"),
    ("The Girl Who Played with Fire", "Stieg Larsson", "9780307949493", "Mystery & Thriller", "Shelf C-14"),
    ("The Girl Who Kicked the Hornet's Nest", "Stieg Larsson", "9780307949509", "Mystery & Thriller", "Shelf C-15"),
    ("Gone Girl", "Gillian Flynn", "9780307588371", "Mystery & Thriller", "Shelf C-16"),
    ("Sharp Objects", "Gillian Flynn", "9780307341556", "Mystery & Thriller", "Shelf C-17"),
    ("Dark Places", "Gillian Flynn", "9780307341570", "Mystery & Thriller", "Shelf C-18"),
    ("The Shining", "Stephen King", "9780307743657", "Mystery & Thriller", "Shelf C-19"),
    ("Misery", "Stephen King", "9781501143106", "Mystery & Thriller", "Shelf C-20"),
    ("It", "Stephen King", "9781501142970", "Mystery & Thriller", "Shelf C-21"),
    ("Carrie", "Stephen King", "9780307743664", "Mystery & Thriller", "Shelf C-22"),
    ("The Stand", "Stephen King", "9780307743688", "Mystery & Thriller", "Shelf C-23"),
    ("Pet Sematary", "Stephen King", "9781501156700", "Mystery & Thriller", "Shelf C-24"),
    ("The Green Mile", "Stephen King", "9781501192265", "Mystery & Thriller", "Shelf C-25"),
    ("11/22/63", "Stephen King", "9781451627299", "Mystery & Thriller", "Shelf C-26"),
    ("The Silence of the Lambs", "Thomas Harris", "9780312924584", "Mystery & Thriller", "Shelf C-27"),
    ("Red Dragon", "Thomas Harris", "9780425228227", "Mystery & Thriller", "Shelf C-28"),
    ("Hannibal", "Thomas Harris", "9780440224679", "Mystery & Thriller", "Shelf C-29"),
    ("The Big Sleep", "Raymond Chandler", "9780394758282", "Mystery & Thriller", "Shelf C-30"),
    ("Farewell, My Lovely", "Raymond Chandler", "9780394758275", "Mystery & Thriller", "Shelf C-31"),
    ("The Long Goodbye", "Raymond Chandler", "9780394757681", "Mystery & Thriller", "Shelf C-32"),
    ("The Maltese Falcon", "Dashiell Hammett", "9780679722649", "Mystery & Thriller", "Shelf C-33"),
    ("Red Harvest", "Dashiell Hammett", "9780679722618", "Mystery & Thriller", "Shelf C-34"),
    ("In Cold Blood", "Truman Capote", "9780679745587", "Mystery & Thriller", "Shelf C-35"),
    ("The Talented Mr. Ripley", "Patricia Highsmith", "9780393332148", "Mystery & Thriller", "Shelf C-36"),
    ("Strangers on a Train", "Patricia Highsmith", "9780393321982", "Mystery & Thriller", "Shelf C-37"),
    ("Tinker Tailor Soldier Spy", "John le Carre", "9780143120933", "Mystery & Thriller", "Shelf C-38"),
    ("The Spy Who Came in from the Cold", "John le Carre", "9780143124757", "Mystery & Thriller", "Shelf C-39"),
    ("Smiley's People", "John le Carre", "9780143120940", "Mystery & Thriller", "Shelf C-40"),
    ("The Constant Gardener", "John le Carre", "9780743287203", "Mystery & Thriller", "Shelf C-41"),
    ("The Bourne Identity", "Robert Ludlum", "9780553593549", "Mystery & Thriller", "Shelf C-42"),
    ("The Bourne Supremacy", "Robert Ludlum", "9780553263220", "Mystery & Thriller", "Shelf C-43"),
    ("The Bourne Ultimatum", "Robert Ludlum", "9780553287738", "Mystery & Thriller", "Shelf C-44"),
    ("The Hunt for Red October", "Tom Clancy", "9780425240335", "Mystery & Thriller", "Shelf C-45"),
    ("Patriot Games", "Tom Clancy", "9780425269404", "Mystery & Thriller", "Shelf C-46"),
    ("Clear and Present Danger", "Tom Clancy", "9780425122730", "Mystery & Thriller", "Shelf C-47"),
    ("The Firm", "John Grisham", "9780440245926", "Mystery & Thriller", "Shelf C-48"),
    ("A Time to Kill", "John Grisham", "9780440245919", "Mystery & Thriller", "Shelf C-49"),
    ("The Pelican Brief", "John Grisham", "9780440245933", "Mystery & Thriller", "Shelf C-50"),
    ("The Client", "John Grisham", "9780440246138", "Mystery & Thriller", "Shelf C-51"),
    ("The Runaway Jury", "John Grisham", "9780440221470", "Mystery & Thriller", "Shelf C-52"),
    ("The Silent Patient", "Alex Michaelides", "9781250301696", "Mystery & Thriller", "Shelf C-53"),
    ("The Maidens", "Alex Michaelides", "9781250304451", "Mystery & Thriller", "Shelf C-54"),
    ("Where the Crawdads Sing", "Delia Owens", "9780735219090", "Mystery & Thriller", "Shelf C-55"),
    ("Big Little Lies", "Liane Moriarty", "9780425274866", "Mystery & Thriller", "Shelf C-56"),
    ("Nine Perfect Strangers", "Liane Moriarty", "9781250069825", "Mystery & Thriller", "Shelf C-57"),
    ("The Woman in the Window", "A.J. Finn", "9780062678423", "Mystery & Thriller", "Shelf C-58"),
    ("The Girl on the Train", "Paula Hawkins", "9781594634024", "Mystery & Thriller", "Shelf C-59"),
    ("Into the Water", "Paula Hawkins", "9780735211209", "Mystery & Thriller", "Shelf C-60"),
    ("Before I Go to Sleep", "S.J. Watson", "9780062060563", "Mystery & Thriller", "Shelf C-61"),
    ("Shutter Island", "Dennis Lehane", "9780061898815", "Mystery & Thriller", "Shelf C-62"),
    ("Mystic River", "Dennis Lehane", "9780062068408", "Mystery & Thriller", "Shelf C-63"),
    ("Live by Night", "Dennis Lehane", "9780060004866", "Mystery & Thriller", "Shelf C-64"),
    ("The Snowman", "Jo Nesbo", "9780307742995", "Mystery & Thriller", "Shelf C-65"),
    ("The Bat", "Jo Nesbo", "9780345807090", "Mystery & Thriller", "Shelf C-66"),
    ("The Redbreast", "Jo Nesbo", "9780061133992", "Mystery & Thriller", "Shelf C-67"),
    ("The Dry", "Jane Harper", "9781250105622", "Mystery & Thriller", "Shelf C-68"),
    ("Force of Nature", "Jane Harper", "9781250105639", "Mystery & Thriller", "Shelf C-69"),
    ("The Lost Man", "Jane Harper", "9781250105684", "Mystery & Thriller", "Shelf C-70"),
    ("Verity", "Colleen Hoover", "9781538724736", "Mystery & Thriller", "Shelf C-71"),
    ("Local Woman Missing", "Mary Kubica", "9780778389446", "Mystery & Thriller", "Shelf C-72"),
    ("The Good Girl", "Mary Kubica", "9780778317333", "Mystery & Thriller", "Shelf C-73"),
    ("The Guest List", "Lucy Foley", "9780062868930", "Mystery & Thriller", "Shelf C-74"),
    ("The Hunting Party", "Lucy Foley", "9780062868909", "Mystery & Thriller", "Shelf C-75"),
    ("The Paris Apartment", "Lucy Foley", "9780063003057", "Mystery & Thriller", "Shelf C-76"),
    ("One by One", "Ruth Ware", "9781501188817", "Mystery & Thriller", "Shelf C-77"),
    ("The Woman in Cabin 10", "Ruth Ware", "9781501132957", "Mystery & Thriller", "Shelf C-78"),
    ("In a Dark, Dark Wood", "Ruth Ware", "9781501112331", "Mystery & Thriller", "Shelf C-79"),
    ("The Turn of the Key", "Ruth Ware", "9781501188770", "Mystery & Thriller", "Shelf C-80"),

    # --- Computer Science & Technology (75 books) ---
    ("Clean Code", "Robert C. Martin", "9780132350884", "Computer Science", "Shelf D-01"),
    ("The Clean Coder", "Robert C. Martin", "9780137081073", "Computer Science", "Shelf D-02"),
    ("Clean Architecture", "Robert C. Martin", "9780134494166", "Computer Science", "Shelf D-03"),
    ("The Pragmatic Programmer", "David Thomas & Andrew Hunt", "9780135957059", "Computer Science", "Shelf D-04"),
    ("Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma et al.", "9780201633610", "Computer Science", "Shelf D-05"),
    ("Refactoring: Improving the Design of Existing Code", "Martin Fowler", "9780134757599", "Computer Science", "Shelf D-06"),
    ("Domain-Driven Design", "Eric Evans", "9780321125217", "Computer Science", "Shelf D-07"),
    ("Structure and Interpretation of Computer Programs", "Harold Abelson & Gerald Jay Sussman", "9780262510875", "Computer Science", "Shelf D-08"),
    ("Introduction to Algorithms (CLRS)", "Thomas H. Cormen et al.", "9780262033848", "Computer Science", "Shelf D-09"),
    ("Algorithms", "Robert Sedgewick & Kevin Wayne", "9780321573513", "Computer Science", "Shelf D-10"),
    ("The Art of Computer Programming, Vol 1", "Donald E. Knuth", "9780201896831", "Computer Science", "Shelf D-11"),
    ("The Art of Computer Programming, Vol 2", "Donald E. Knuth", "9780201896848", "Computer Science", "Shelf D-12"),
    ("The Art of Computer Programming, Vol 3", "Donald E. Knuth", "9780201896855", "Computer Science", "Shelf D-13"),
    ("The Mythical Man-Month", "Frederick P. Brooks Jr.", "9780201835953", "Computer Science", "Shelf D-14"),
    ("Code Complete", "Steve McConnell", "9780735619678", "Computer Science", "Shelf D-15"),
    ("Code: The Hidden Language of Computer Hardware and Software", "Charles Petzold", "9780735611313", "Computer Science", "Shelf D-16"),
    ("You Don't Know JS: Scope & Closures", "Kyle Simpson", "9781449335588", "Computer Science", "Shelf D-17"),
    ("Eloquent JavaScript", "Marijn Haverbeke", "9781593279509", "Computer Science", "Shelf D-18"),
    ("JavaScript: The Good Parts", "Douglas Crockford", "9780596517748", "Computer Science", "Shelf D-19"),
    ("Effective Python", "Brett Slatkin", "9780134853987", "Computer Science", "Shelf D-20"),
    ("Fluent Python", "Luciano Ramalho", "9781491946008", "Computer Science", "Shelf D-21"),
    ("Python Crash Course", "Eric Matthes", "9781593279288", "Computer Science", "Shelf D-22"),
    ("Automate the Boring Stuff with Python", "Al Sweigart", "9781593279929", "Computer Science", "Shelf D-23"),
    ("Learning Python", "Mark Lutz", "9781449355739", "Computer Science", "Shelf D-24"),
    ("Python Cookbook", "David Beazley & Brian K. Jones", "9781449340377", "Computer Science", "Shelf D-25"),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "9781449373320", "Computer Science", "Shelf D-26"),
    ("Database System Concepts", "Abraham Silberschatz et al.", "9780073523323", "Computer Science", "Shelf D-27"),
    ("SQL Antipatterns", "Bill Karwin", "9781934356555", "Computer Science", "Shelf D-28"),
    ("High Performance MySQL", "Baron Schwartz et al.", "9781449314002", "Computer Science", "Shelf D-29"),
    ("Operating System Concepts", "Abraham Silberschatz et al.", "9781119800361", "Computer Science", "Shelf D-30"),
    ("Modern Operating Systems", "Andrew S. Tanenbaum", "9780133591620", "Computer Science", "Shelf D-31"),
    ("Computer Networks", "Andrew S. Tanenbaum & David J. Wetherall", "9780132126953", "Computer Science", "Shelf D-32"),
    ("Computer Systems: A Programmer's Perspective", "Randal E. Bryant & David R. O'Hallaron", "9780134092669", "Computer Science", "Shelf D-33"),
    ("Site Reliability Engineering", "Betsy Beyer et al. (Google)", "9781491929124", "Computer Science", "Shelf D-34"),
    ("The Phoenix Project", "Gene Kim, Kevin Behr & George Spafford", "9781942788294", "Computer Science", "Shelf D-35"),
    ("The DevOps Handbook", "Gene Kim et al.", "9781942788003", "Computer Science", "Shelf D-36"),
    ("Accelerate: Building and Scaling High Performing Technology", "Nicole Forsgren et al.", "9781942788331", "Computer Science", "Shelf D-37"),
    ("Building Microservices", "Sam Newman", "9781492034025", "Computer Science", "Shelf D-38"),
    ("Monolith to Microservices", "Sam Newman", "9781492047841", "Computer Science", "Shelf D-39"),
    ("Continuous Delivery", "Jez Humble & David Farley", "9780321601919", "Computer Science", "Shelf D-40"),
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "9780984782857", "Computer Science", "Shelf D-41"),
    ("Elements of Programming Interviews in Python", "Adnan Aziz et al.", "9781537713946", "Computer Science", "Shelf D-42"),
    ("Grokking Algorithms", "Aditya Bhargava", "9781617292231", "Computer Science", "Shelf D-43"),
    ("Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "Aurelien Geron", "9781492032649", "Computer Science", "Shelf D-44"),
    ("Pattern Recognition and Machine Learning", "Christopher M. Bishop", "9780387310732", "Computer Science", "Shelf D-45"),
    ("Deep Learning", "Ian Goodfellow, Yoshua Bengio & Aaron Courville", "9780262035613", "Computer Science", "Shelf D-46"),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell & Peter Norvig", "9780134610993", "Computer Science", "Shelf D-47"),
    ("The C Programming Language", "Brian W. Kernighan & Dennis M. Ritchie", "9780131103627", "Computer Science", "Shelf D-48"),
    ("The Practice of Programming", "Brian W. Kernighan & Rob Pike", "9780201615869", "Computer Science", "Shelf D-49"),
    ("The Linux Programming Interface", "Michael Kerrisk", "9781593272203", "Computer Science", "Shelf D-50"),
    ("Linux Kernel Development", "Robert Love", "9780672329463", "Computer Science", "Shelf D-51"),
    ("TCP/IP Illustrated, Vol. 1", "W. Richard Stevens", "9780321336316", "Computer Science", "Shelf D-52"),
    ("Unix and Linux System Administration Handbook", "Evi Nemeth et al.", "9780134277554", "Computer Science", "Shelf D-53"),
    ("Pro Git", "Scott Chacon & Ben Straub", "9781484200773", "Computer Science", "Shelf D-54"),
    ("Working Effectively with Legacy Code", "Michael Feathers", "9780131177055", "Computer Science", "Shelf D-55"),
    ("Test Driven Development: By Example", "Kent Beck", "9780321146533", "Computer Science", "Shelf D-56"),
    ("Extreme Programming Explained", "Kent Beck", "9780321278654", "Computer Science", "Shelf D-57"),
    ("Patterns of Enterprise Application Architecture", "Martin Fowler", "9780321127426", "Computer Science", "Shelf D-58"),
    ("Enterprise Integration Patterns", "Gregor Hohpe & Bobby Woolf", "9780321200686", "Computer Science", "Shelf D-59"),
    ("Release It!: Design and Deploy Production-Ready Software", "Michael T. Nygard", "9781680502398", "Computer Science", "Shelf D-60"),
    ("Effective Java", "Joshua Bloch", "9780134685991", "Computer Science", "Shelf D-61"),
    ("Java Concurrency in Practice", "Brian Goetz et al.", "9780321349606", "Computer Science", "Shelf D-62"),
    ("C++ Primer", "Stanley B. Lippman et al.", "9780321714114", "Computer Science", "Shelf D-63"),
    ("Effective Modern C++", "Scott Meyers", "9781491903995", "Computer Science", "Shelf D-64"),
    ("The Rust Programming Language", "Steve Klabnik & Carol Nichols", "9781593278281", "Computer Science", "Shelf D-65"),
    ("Programming Rust", "Jim Blandy & Jason Orendorff", "9781491927281", "Computer Science", "Shelf D-66"),
    ("The Go Programming Language", "Alan A. A. Donovan & Brian W. Kernighan", "9780134190440", "Computer Science", "Shelf D-67"),
    ("Kubernetes in Action", "Marko Luksa", "9781617293726", "Computer Science", "Shelf D-68"),
    ("Docker in Action", "Jeff Nickoloff & Stephen Kuenzli", "9781617294761", "Computer Science", "Shelf D-69"),
    ("Terraform: Up & Running", "Yevgeniy Brikman", "9781492046905", "Computer Science", "Shelf D-70"),
    ("Web Application Security", "Andrew Hoffman", "9781492053118", "Computer Science", "Shelf D-71"),
    ("The Tangled Web: A Guide to Securing Modern Web Applications", "Michal Zalewski", "9781593273880", "Computer Science", "Shelf D-72"),
    ("Practical Malware Analysis", "Michael Sikorski & Andrew Honig", "9781593272906", "Computer Science", "Shelf D-73"),
    ("Hacking: The Art of Exploitation", "Jon Erickson", "9781593271442", "Computer Science", "Shelf D-74"),
    ("Silence on the Wire", "Michal Zalewski", "9781593270469", "Computer Science", "Shelf D-75"),

    # --- Science, History & Non-Fiction (85 books) ---
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "9780062316097", "Non-Fiction", "Shelf E-01"),
    ("Homo Deus: A Brief History of Tomorrow", "Yuval Noah Harari", "9780062464316", "Non-Fiction", "Shelf E-02"),
    ("21 Lessons for the 21st Century", "Yuval Noah Harari", "9780525512172", "Non-Fiction", "Shelf E-03"),
    ("A Brief History of Time", "Stephen Hawking", "9780553380163", "Non-Fiction", "Shelf E-04"),
    ("The Grand Design", "Stephen Hawking & Leonard Mlodinow", "9780553384666", "Non-Fiction", "Shelf E-05"),
    ("Cosmos", "Carl Sagan", "9780345539434", "Non-Fiction", "Shelf E-06"),
    ("Pale Blue Dot", "Carl Sagan", "9780345376596", "Non-Fiction", "Shelf E-07"),
    ("The Demon-Haunted World", "Carl Sagan", "9780345409461", "Non-Fiction", "Shelf E-08"),
    ("The Selfish Gene", "Richard Dawkins", "9780199291151", "Non-Fiction", "Shelf E-09"),
    ("The Blind Watchmaker", "Richard Dawkins", "9780393315707", "Non-Fiction", "Shelf E-10"),
    ("The God Delusion", "Richard Dawkins", "9780618918249", "Non-Fiction", "Shelf E-11"),
    ("Surely You're Joking, Mr. Feynman!", "Richard P. Feynman", "9780393316049", "Non-Fiction", "Shelf E-12"),
    ("What Do You Care What Other People Think?", "Richard P. Feynman", "9780393320923", "Non-Fiction", "Shelf E-13"),
    ("A Short History of Nearly Everything", "Bill Bryson", "9780767908184", "Non-Fiction", "Shelf E-14"),
    ("The Body: A Guide for Occupants", "Bill Bryson", "9780385539999", "Non-Fiction", "Shelf E-15"),
    ("Guns, Germs, and Steel", "Jared Diamond", "9780393317558", "Non-Fiction", "Shelf E-16"),
    ("Collapse: How Societies Choose to Fail or Succeed", "Jared Diamond", "9780143117001", "Non-Fiction", "Shelf E-17"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "9780374533557", "Non-Fiction", "Shelf E-18"),
    ("Nudge", "Richard H. Thaler & Cass R. Sunstein", "9780143115267", "Non-Fiction", "Shelf E-19"),
    ("Misbehaving: The Making of Behavioral Economics", "Richard H. Thaler", "9780393352795", "Non-Fiction", "Shelf E-20"),
    ("Outliers: The Story of Success", "Malcolm Gladwell", "9780316017930", "Non-Fiction", "Shelf E-21"),
    ("The Tipping Point", "Malcolm Gladwell", "9780316346627", "Non-Fiction", "Shelf E-22"),
    ("Blink: The Power of Thinking Without Thinking", "Malcolm Gladwell", "9780316010665", "Non-Fiction", "Shelf E-23"),
    ("Quiet: The Power of Introverts in a World That Can't Stop Talking", "Susan Cain", "9780307352156", "Non-Fiction", "Shelf E-24"),
    ("Educated", "Tara Westover", "9780399590504", "Non-Fiction", "Shelf E-25"),
    ("Becoming", "Michelle Obama", "9781524763138", "Non-Fiction", "Shelf E-26"),
    ("Steve Jobs", "Walter Isaacson", "9781451648539", "Non-Fiction", "Shelf E-27"),
    ("Einstein: His Life and Universe", "Walter Isaacson", "9780743264747", "Non-Fiction", "Shelf E-28"),
    ("Leonardo da Vinci", "Walter Isaacson", "9781501139154", "Non-Fiction", "Shelf E-29"),
    ("The Innovators", "Walter Isaacson", "9781476708690", "Non-Fiction", "Shelf E-30"),
    ("The Gene: An Intimate History", "Siddhartha Mukherjee", "9781476733500", "Non-Fiction", "Shelf E-31"),
    ("The Emperor of All Maladies", "Siddhartha Mukherjee", "9781439170915", "Non-Fiction", "Shelf E-32"),
    ("When Breath Becomes Air", "Paul Kalanithi", "9780812988406", "Non-Fiction", "Shelf E-33"),
    ("The Immortal Life of Henrietta Lacks", "Rebecca Skloot", "9781400052189", "Non-Fiction", "Shelf E-34"),
    ("Born a Crime", "Trevor Noah", "9780399588174", "Non-Fiction", "Shelf E-35"),
    ("Bad Blood: Secrets and Lies in a Silicon Valley Startup", "John Carreyrou", "9781524731656", "Non-Fiction", "Shelf E-36"),
    ("Zero to One", "Peter Thiel & Blake Masters", "9780804139298", "Non-Fiction", "Shelf E-37"),
    ("The Lean Startup", "Eric Ries", "9780307887894", "Non-Fiction", "Shelf E-38"),
    ("Good to Great", "Jim Collins", "9780066620992", "Non-Fiction", "Shelf E-39"),
    ("The Hard Thing About Hard Things", "Ben Horowitz", "9780062273208", "Non-Fiction", "Shelf E-40"),
    ("Freakonomics", "Steven D. Levitt & Stephen J. Dubner", "9780060731335", "Non-Fiction", "Shelf E-41"),
    ("SuperFreakonomics", "Steven D. Levitt & Stephen J. Dubner", "9780060889579", "Non-Fiction", "Shelf E-42"),
    ("Predictably Irrational", "Dan Ariely", "9780061353246", "Non-Fiction", "Shelf E-43"),
    ("The Black Swan", "Nassim Nicholas Taleb", "9781400063512", "Non-Fiction", "Shelf E-44"),
    ("Antifragile: Things That Gain from Disorder", "Nassim Nicholas Taleb", "9781400067824", "Non-Fiction", "Shelf E-45"),
    ("Fooled by Randomness", "Nassim Nicholas Taleb", "9780812975215", "Non-Fiction", "Shelf E-46"),
    ("Skin in the Game", "Nassim Nicholas Taleb", "9780425284629", "Non-Fiction", "Shelf E-47"),
    ("Factfulness", "Hans Rosling", "9781250107817", "Non-Fiction", "Shelf E-48"),
    ("Enlightenment Now", "Steven Pinker", "9780525427575", "Non-Fiction", "Shelf E-49"),
    ("The Better Angels of Our Nature", "Steven Pinker", "9780143122012", "Non-Fiction", "Shelf E-50"),
    ("The Blank Slate", "Steven Pinker", "9780142003343", "Non-Fiction", "Shelf E-51"),
    ("The Righteous Mind", "Jonathan Haidt", "9780307455772", "Non-Fiction", "Shelf E-52"),
    ("The Coddling of the American Mind", "Jonathan Haidt & Greg Lukianoff", "9780735224896", "Non-Fiction", "Shelf E-53"),
    ("Flow: The Psychology of Optimal Experience", "Mihaly Csikszentmihalyi", "9780061339202", "Non-Fiction", "Shelf E-54"),
    ("Man's Search for Meaning", "Viktor E. Frankl", "9780807014295", "Non-Fiction", "Shelf E-55"),
    ("Atomic Habits", "James Clear", "9780735211292", "Non-Fiction", "Shelf E-56"),
    ("Deep Work", "Cal Newport", "9781455586691", "Non-Fiction", "Shelf E-57"),
    ("Digital Minimalism", "Cal Newport", "9780525536512", "Non-Fiction", "Shelf E-58"),
    ("So Good They Can't Ignore You", "Cal Newport", "9781455509126", "Non-Fiction", "Shelf E-59"),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", "9781982137274", "Non-Fiction", "Shelf E-60"),
    ("How to Win Friends and Influence People", "Dale Carnegie", "9780671027032", "Non-Fiction", "Shelf E-61"),
    ("Principles: Life and Work", "Ray Dalio", "9781501124020", "Non-Fiction", "Shelf E-62"),
    ("The Psychology of Money", "Morgan Housel", "9780857197689", "Non-Fiction", "Shelf E-63"),
    ("Rich Dad Poor Dad", "Robert T. Kiyosaki", "9781612680194", "Non-Fiction", "Shelf E-64"),
    ("The Intelligent Investor", "Benjamin Graham", "9780060555665", "Non-Fiction", "Shelf E-65"),
    ("A Random Walk Down Wall Street", "Burton G. Malkiel", "9780393358322", "Non-Fiction", "Shelf E-66"),
    ("Common Stocks and Uncommon Profits", "Philip A. Fisher", "9780471445500", "Non-Fiction", "Shelf E-67"),
    ("One Up On Wall Street", "Peter Lynch", "9780743200400", "Non-Fiction", "Shelf E-68"),
    ("Poor Charlie's Almanack", "Charles T. Munger", "9781578645015", "Non-Fiction", "Shelf E-69"),
    ("Shoe Dog: A Memoir by the Creator of Nike", "Phil Knight", "9781501135910", "Non-Fiction", "Shelf E-70"),
    ("Open: An Autobiography", "Andre Agassi", "9780307388407", "Non-Fiction", "Shelf E-71"),
    ("Titan: The Life of John D. Rockefeller, Sr.", "Ron Chernow", "9781400077304", "Non-Fiction", "Shelf E-72"),
    ("Alexander Hamilton", "Ron Chernow", "9780143034759", "Non-Fiction", "Shelf E-73"),
    ("Washington: A Life", "Ron Chernow", "9780143119968", "Non-Fiction", "Shelf E-74"),
    ("Grant", "Ron Chernow", "9780143110637", "Non-Fiction", "Shelf E-75"),
    ("Team of Rivals: The Political Genius of Abraham Lincoln", "Doris Kearns Goodwin", "9780743270755", "Non-Fiction", "Shelf E-76"),
    ("The Wright Brothers", "David McCullough", "9781476728742", "Non-Fiction", "Shelf E-77"),
    ("John Adams", "David McCullough", "9780684813639", "Non-Fiction", "Shelf E-78"),
    ("1776", "David McCullough", "9780743226714", "Non-Fiction", "Shelf E-79"),
    ("Gombrich: A Little History of the World", "E.H. Gombrich", "9780300143324", "Non-Fiction", "Shelf E-80"),
    ("The Story of Art", "E.H. Gombrich", "9780714832470", "Non-Fiction", "Shelf E-81"),
    ("A People's History of the United States", "Howard Zinn", "9780062397348", "Non-Fiction", "Shelf E-82"),
    ("The Silk Roads: A New History of the World", "Peter Frankopan", "9781101912379", "Non-Fiction", "Shelf E-83"),
    ("Postwar: A History of Europe Since 1945", "Tony Judt", "9780143037750", "Non-Fiction", "Shelf E-84"),
    ("The Rise and Fall of the Third Reich", "William L. Shirer", "9781451651683", "Non-Fiction", "Shelf E-85"),

    # --- Philosophy & Self-Growth (65 books) ---
    ("Meditations", "Marcus Aurelius", "9780140449334", "Philosophy", "Shelf F-01"),
    ("Letters from a Stoic", "Seneca", "9780140442106", "Philosophy", "Shelf F-02"),
    ("Discourses and Selected Writings", "Epictetus", "9780140449464", "Philosophy", "Shelf F-03"),
    ("The Republic", "Plato", "9780140455113", "Philosophy", "Shelf F-04"),
    ("Symposium", "Plato", "9780140449273", "Philosophy", "Shelf F-05"),
    ("Nicomachean Ethics", "Aristotle", "9780140449495", "Philosophy", "Shelf F-06"),
    ("Politics", "Aristotle", "9780140444216", "Philosophy", "Shelf F-07"),
    ("The Prince", "Niccolo Machiavelli", "9780140449150", "Philosophy", "Shelf F-08"),
    ("Leviathan", "Thomas Hobbes", "9780140431957", "Philosophy", "Shelf F-09"),
    ("Two Treatises of Government", "John Locke", "9780521357302", "Philosophy", "Shelf F-10"),
    ("The Social Contract", "Jean-Jacques Rousseau", "9780140442014", "Philosophy", "Shelf F-11"),
    ("Critique of Pure Reason", "Immanuel Kant", "9780521657297", "Philosophy", "Shelf F-12"),
    ("Beyond Good and Evil", "Friedrich Nietzsche", "9780140449235", "Philosophy", "Shelf F-13"),
    ("Thus Spoke Zarathustra", "Friedrich Nietzsche", "9780140441185", "Philosophy", "Shelf F-14"),
    ("The Genealogy of Morals", "Friedrich Nietzsche", "9780141195377", "Philosophy", "Shelf F-15"),
    ("The Art of War", "Sun Tzu", "9781590302255", "Philosophy", "Shelf F-16"),
    ("Tao Te Ching", "Lao Tzu", "9780140441313", "Philosophy", "Shelf F-17"),
    ("The Book of Five Rings", "Miyamoto Musashi", "9781590302484", "Philosophy", "Shelf F-18"),
    ("The Daily Stoic", "Ryan Holiday & Stephen Hanselman", "9780735211735", "Philosophy", "Shelf F-19"),
    ("The Obstacle Is the Way", "Ryan Holiday", "9781591846352", "Philosophy", "Shelf F-20"),
    ("Ego Is the Enemy", "Ryan Holiday", "9781591847816", "Philosophy", "Shelf F-21"),
    ("Stillness Is the Key", "Ryan Holiday", "9780525538585", "Philosophy", "Shelf F-22"),
    ("Courage Is Calling", "Ryan Holiday", "9780593191675", "Philosophy", "Shelf F-23"),
    ("Discipline Is Destiny", "Ryan Holiday", "9780593191699", "Philosophy", "Shelf F-24"),
    ("Right Thing, Right Now", "Ryan Holiday", "9780593191712", "Philosophy", "Shelf F-25"),
    ("The Power of Now", "Eckhart Tolle", "9781577314806", "Philosophy", "Shelf F-26"),
    ("A New Earth", "Eckhart Tolle", "9780452289963", "Philosophy", "Shelf F-27"),
    ("Waking Up: A Guide to Spirituality Without Religion", "Sam Harris", "9781451636024", "Philosophy", "Shelf F-28"),
    ("Free Will", "Sam Harris", "9781451683400", "Philosophy", "Shelf F-29"),
    ("Lying", "Sam Harris", "9781940051000", "Philosophy", "Shelf F-30"),
    ("12 Rules for Life: An Antidote to Chaos", "Jordan B. Peterson", "9780345816023", "Philosophy", "Shelf F-31"),
    ("Beyond Order: 12 More Rules for Life", "Jordan B. Peterson", "9780593084649", "Philosophy", "Shelf F-32"),
    ("Grit: The Power of Passion and Perseverance", "Angela Duckworth", "9781501111105", "Philosophy", "Shelf F-33"),
    ("Mindset: The New Psychology of Success", "Carol S. Dweck", "9780345472327", "Philosophy", "Shelf F-34"),
    ("Can't Hurt Me: Master Your Mind and Defy the Odds", "David Goggins", "9781544512273", "Philosophy", "Shelf F-35"),
    ("Never Finished", "David Goggins", "9781544534077", "Philosophy", "Shelf F-36"),
    ("The 48 Laws of Power", "Robert Greene", "9780140280197", "Philosophy", "Shelf F-37"),
    ("The Laws of Human Nature", "Robert Greene", "9780525428145", "Philosophy", "Shelf F-38"),
    ("Mastery", "Robert Greene", "9780143124177", "Philosophy", "Shelf F-39"),
    ("The 33 Strategies of War", "Robert Greene", "9780143112785", "Philosophy", "Shelf F-40"),
    ("The Art of Seduction", "Robert Greene", "9780142001196", "Philosophy", "Shelf F-41"),
    ("The Four Agreements", "Don Miguel Ruiz", "9781878424310", "Philosophy", "Shelf F-42"),
    ("The Mastery of Love", "Don Miguel Ruiz", "9781878424426", "Philosophy", "Shelf F-43"),
    ("The Voice of Knowledge", "Don Miguel Ruiz", "9781878424549", "Philosophy", "Shelf F-44"),
    ("Daring Greatly", "Brene Brown", "9781592408412", "Philosophy", "Shelf F-45"),
    ("The Gifts of Imperfection", "Brene Brown", "9781592858491", "Philosophy", "Shelf F-46"),
    ("Braving the Wilderness", "Brene Brown", "9780812995848", "Philosophy", "Shelf F-47"),
    ("Dare to Lead", "Brene Brown", "9780399592522", "Philosophy", "Shelf F-48"),
    ("Essentialism: The Disciplined Pursuit of Less", "Greg McKeown", "9780804137386", "Philosophy", "Shelf F-49"),
    ("Effortless: Make It Easier to Do What Matters Most", "Greg McKeown", "9780593135648", "Philosophy", "Shelf F-50"),
    ("Make Time: How to Focus on What Matters Every Day", "Jake Knapp & John Zeratsky", "9780525572428", "Philosophy", "Shelf F-51"),
    ("Sprint: How to Solve Big Problems and Test New Ideas in Just Five Days", "Jake Knapp", "9781501121746", "Philosophy", "Shelf F-52"),
    ("Show Your Work!", "Austin Kleon", "9780761178972", "Philosophy", "Shelf F-53"),
    ("Steal Like an Artist", "Austin Kleon", "9780761169253", "Philosophy", "Shelf F-54"),
    ("Keep Going", "Austin Kleon", "9781523506644", "Philosophy", "Shelf F-55"),
    ("The War of Art", "Steven Pressfield", "9781936891023", "Philosophy", "Shelf F-56"),
    ("Turning Pro", "Steven Pressfield", "9781936891030", "Philosophy", "Shelf F-57"),
    ("Nobody Wants to Read Your Sh*t", "Steven Pressfield", "9781936891498", "Philosophy", "Shelf F-58"),
    ("A Guide to the Good Life: The Ancient Art of Stoic Joy", "William B. Irvine", "9780195374612", "Philosophy", "Shelf F-59"),
    ("Breakfast with Seneca", "David Fideler", "9781324005155", "Philosophy", "Shelf F-60"),
    ("How to Think Like a Roman Emperor", "Donald Robertson", "9781250196620", "Philosophy", "Shelf F-61"),
    ("Philosophy as a Way of Life", "Pierre Hadot", "9780631180333", "Philosophy", "Shelf F-62"),
    ("At the Existentialist Cafe", "Sarah Bakewell", "9781590518885", "Philosophy", "Shelf F-63"),
    ("How to Live: A Life of Montaigne", "Sarah Bakewell", "9781590514832", "Philosophy", "Shelf F-64"),
    ("Justice: What's the Right Thing to Do?", "Michael J. Sandel", "9780374532505", "Philosophy", "Shelf F-65"),
]

# Ensure we have exactly 500 books by generating extra physical copies
# (Simulating real libraries having 2 or 3 copies of popular books)
def build_500_inventory():
    inventory = []
    # Add unique title base (about 500 total copies)
    for b in CURATED_BOOKS:
        inventory.append(b)

    # Some titles have duplicate physical copies
    idx = 0
    copy_counter = 2
    while len(inventory) < 500:
        base = CURATED_BOOKS[idx % len(CURATED_BOOKS)]
        shelf = base[4] + f"-c{copy_counter}"
        inventory.append((base[0], base[1], base[2], base[3], shelf))
        idx += 1
        if idx % len(CURATED_BOOKS) == 0:
            copy_counter += 1

    return inventory[:500]


# ----------------------------------------------------------------------
# Sample Members
# ----------------------------------------------------------------------
SAMPLE_MEMBERS = [
    ("Alice Smith", "alice.smith@university.edu", "+1-555-0101", "Student", 3),
    ("Dr. Brian Clark", "bclark@university.edu", "+1-555-0102", "Faculty", 10),
    ("Catherine Davis", "catherine.d@gmail.com", "+1-555-0103", "General Public", 2),
    ("Daniel Evans", "daniel.evans@college.edu", "+1-555-0104", "Student", 3),
    ("Emma Watson", "emma.w@research.org", "+1-555-0105", "Researcher", 8),
    ("Farhan Khan", "farhan.khan@tech.edu", "+1-555-0106", "Student", 3),
    ("Grace Hopper", "grace.h@computing.org", "+1-555-0107", "Faculty", 10),
    ("Henry Miller", "henry.m@literature.net", "+1-555-0108", "General Public", 2),
]


def seed_database():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop old tables to migrate to upgraded schema cleanly
    cursor.execute("DROP TABLE IF EXISTS loans")
    cursor.execute("DROP TABLE IF EXISTS members")
    cursor.execute("DROP TABLE IF EXISTS books")

    # Create tables with comprehensive upgraded schema
    cursor.execute(
        """
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            genre TEXT DEFAULT 'General',
            shelf_location TEXT DEFAULT 'Shelf A-01',
            cover_url TEXT,
            status TEXT NOT NULL DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            member_type TEXT DEFAULT 'Student',
            max_books INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            fine_amount REAL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
        """
    )
    conn.commit()

    # Check existing books count
    cursor.execute("SELECT COUNT(*) FROM books")
    current_count = cursor.fetchone()[0]

    if current_count < 500:
        print(f"Clearing and re-populating with 500 curated books...")
        cursor.execute("DELETE FROM loans")
        cursor.execute("DELETE FROM books")
        cursor.execute("DELETE FROM members")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('books', 'members', 'loans')")
        conn.commit()

        # Insert 500 books
        books_500 = build_500_inventory()
        for title, author, isbn, genre, shelf in books_500:
            cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn else ""
            cursor.execute(
                """
                INSERT INTO books (title, author, isbn, genre, shelf_location, cover_url, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Available')
                """,
                (title, author, isbn, genre, shelf, cover),
            )
        conn.commit()
        print(f"Successfully seeded {len(books_500)} books!")

        # Insert sample members
        for name, email, phone, mtype, max_b in SAMPLE_MEMBERS:
            cursor.execute(
                """
                INSERT INTO members (name, email, phone, member_type, max_books)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, email, phone, mtype, max_b),
            )
        conn.commit()
        print(f"Successfully seeded {len(SAMPLE_MEMBERS)} library members!")

        # Create active and overdue sample loans
        today = datetime.now()

        sample_loans_spec = [
            # (book_id, member_id, days_ago_issued, days_until_due, status)
            (1, 1, 4, 10, "Active"),           # Due in 10 days
            (2, 2, 7, 7, "Active"),            # Due in 7 days
            (3, 3, 2, 12, "Active"),           # Due in 12 days
            (4, 4, 25, -11, "Overdue"),        # 11 days overdue! ($5.50 fine)
            (5, 5, 20, -6, "Overdue"),         # 6 days overdue! ($3.00 fine)
            (6, 6, 18, -4, "Overdue"),         # 4 days overdue! ($2.00 fine)
            (7, 1, 14, 0, "Active"),           # Due today
            (8, 2, 10, 4, "Active"),           # Due in 4 days
            (9, 3, 30, -16, "Overdue"),        # 16 days overdue! ($8.00 fine)
            (10, 7, 5, 9, "Active"),           # Due in 9 days
        ]

        for book_id, member_id, issued_ago, due_diff, loan_status in sample_loans_spec:
            issue_date = (today - timedelta(days=issued_ago)).strftime("%Y-%m-%d")
            due_date = (today + timedelta(days=due_diff)).strftime("%Y-%m-%d")

            fine = 0.0
            if due_diff < 0:
                fine = round(abs(due_diff) * 0.50, 2)  # $0.50 per day overdue

            cursor.execute(
                """
                INSERT INTO loans (book_id, member_id, issue_date, due_date, fine_amount, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (book_id, member_id, issue_date, due_date, fine, loan_status),
            )

            # Mark book as Issued
            cursor.execute("UPDATE books SET status = 'Issued' WHERE id = ?", (book_id,))

        conn.commit()
        print("Successfully seeded realistic active and overdue loans!")
    else:
        print(f"Database already contains {current_count} books. Skipping seeding.")

    conn.close()
    print("Database seeding completed.")


if __name__ == "__main__":
    seed_database()
