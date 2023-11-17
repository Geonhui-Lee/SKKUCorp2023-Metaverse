conversation_documents = [
    {
		"node": 1,
		"name": "user0",
		"opponent": "Police Officer",
		"memory": "Halo"
	},
	{
		"node": 2,
		"name": "user0",
		"opponent": "Police Officer",
		"memory": "I think you are cute"
	},
	{
		"node": 3,
		"name": "user0",
		"opponent": "Police Officer",
		"memory": "My name is Geonhui"
	},
	{
		"node": 4,
		"name": "user0",
		"opponent": "Police Officer",
		"memory": "Nice to meet you"
	},
	{
		"node": 5,
		"name": "user0",
		"opponent": "Police Officer",
		"memory": "What are you name?"
	}
]
cefr_documents = []
retrieve_documents = [{
	"name": "Police Officer",
	"retrieve": "The user struggles with grammar and spelling, as seen in statements [1] and [5]."
}]
reflect_documents = [{
    "name": "Police Officer",
    "reflect": "Insight: User0 is interested in becoming a police officer. (because of statements 5, 8, and 35)\n2. Insight: User0 is curious about firearms and their purpose. (because of statements 10, 12, 20, and 22)\n3. Insight: User0 is seeking information about communication. (because of statement 1)\n4. Insight: User0 is asking about the role and importance of police officers. (because of statement 34)\n5. Insight: User0 is inquiring about the use of firearms by police officers. (because of statements 12, 20, 22, and 26)"
}]