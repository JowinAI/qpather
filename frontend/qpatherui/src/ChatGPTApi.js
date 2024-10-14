import axios from 'axios';

// Replace with your OpenAI API key
const API_KEY = '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';

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
