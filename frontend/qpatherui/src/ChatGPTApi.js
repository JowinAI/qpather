import axios from 'axios';

// Replace with your OpenAI API key
const API_KEY = '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';
const personDetails = {
  role: "Responsible for the Henkel Adhesive Industrial's SBU America’s and Global Telecom, Power and Solar Segments.Highly motivated and experienced business leader with expert proficiency in providing unsurpassed leadership and revenue growth in a dynamic, fast paced, competitive business environment, consistently rated as a top performer within the global organization. Offers expertise in P&L management, marketing leadership, engineering, operations, and technology management.",
  company: "Henkel operates worldwide with leading innovations, brands and technologies in two business areas: Adhesive Technologies and Consumer Brands.",
  geography: "North America"
};
// Function to send context, content, and instruction to ChatGPT
export const getChatGPTResponse = async (context, content, instruction) => {
  const prompt = `
    Context: ${context}
    Content: ${content}
    Instruction: ${instruction}
  `;

  try {
    // const response = await axios.post(
    //   'https://api.openai.com/v1/chat/completions',  // Correct endpoint
    //   {
    //     model: 'gpt-3.5-turbo',
    //     messages: [
    //       { role: 'system', content: context },   // For system context
    //       { role: 'user', content: content },     // User input
    //       { role: 'assistant', content: instruction }  // Instruction, if needed
    //     ],
    //     max_tokens: 200, // Adjust based on the length of response needed
    //     temperature: 0.7,
    //   },
    //   {
    //     headers: {
    //       'Content-Type': 'application/json',
    //       Authorization: `Bearer ${API_KEY}`,
    //     },
    //   }
    // );

    // Process the response as per your instruction
   // const responseText = response.data.choices[0].message.content;

   //alert(JSON.parse(responseText));
    // If the instruction is to return a JSON array, assume it's in the response
    const questions = [
      "What data do we have on previous sales trends?",
      "Have we identified any seasonal patterns or cyclical trends in sales?",
      "Are there any external factors that could impact sales in the next quarter?",
      "Have we considered the impact of any recent marketing or sales initiatives on future sales?",
      "Do we have any forecasts or predictions from industry experts or analysts that could help inform our sales predictions?"
  ];//JSON.parse(responseText); // Adjust parsing if necessary
    
    return questions;
  } catch (error) {
    console.error('Error fetching response from ChatGPT:', error);
    return [];
  }
};


export const getChatGPTResponse2 = async (content) => {
  // Construct the system message with person's details and expected response format
  const systemMessage = `
    You are assisting a user from the following context:
    - Role: ${personDetails.role}
    - Company: ${personDetails.company}
    - Company Geography: ${personDetails.geography}

    Please provide responses based on the user's background.

    The response must be in the following JSON format:
    {
      "Goal": "one title line for what the user is trying to achieve",
      "Questions": [
        "your first question",
        "your second question",
        ...
      ]
    }
  `;

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: systemMessage },  // System message with instructions
          { role: 'user', content: content },          // User's query
        ],
        max_tokens: 200, // Adjust based on the length of response needed
        temperature: 0.7,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${API_KEY}`,
        },
      }
    );

    // Process the response
    const responseText = response.data.choices[0].message.content;
    alert(responseText);
    return JSON.parse(responseText);  // Return the formatted JSON response
  } catch (error) {
    console.error('Error in calling OpenAI API:', error);
    throw error;  // Handle the error appropriately
  }
};