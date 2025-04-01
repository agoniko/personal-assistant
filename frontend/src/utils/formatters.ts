interface EmailData {
  from: string;
  date: string;
  subject: string;
  content: string;
}

interface CalendarEvent {
  event: string;
  location: string;
  time: string;
}

export const formatEmail = (email: EmailData): string => {
  return `📧 ${email.from}\n` +
         `📅 ${email.date}\n` +
         `📌 ${email.subject}\n\n` +
         `${email.content}`;
};

export const formatCalendarEvents = (events: CalendarEvent[]): string => {
  return events.map((event, index) => {
    return `${index + 1}. 📅 ${event.event}\n` +
           `   📍 ${event.location}\n` +
           `   ⏰ ${event.time}\n`;
  }).join('\n');
};

export const parseEmailFromText = (text: string): EmailData | null => {
  try {
    const fromMatch = text.match(/\*\*From\*\*: (.*?)(?=\s*-\s*\*\*Date\*\*:)/s);
    const dateMatch = text.match(/\*\*Date\*\*: (.*?)(?=\s*-\s*\*\*Subject\*\*:)/s);
    const subjectMatch = text.match(/\*\*Subject\*\*: (.*?)(?=\s*-\s*\*\*Content\*\*:)/s);
    const contentMatch = text.match(/\*\*Content\*\*: (.*?)$/s);

    if (!fromMatch || !dateMatch || !subjectMatch || !contentMatch) {
      return null;
    }

    return {
      from: fromMatch[1].trim(),
      date: dateMatch[1].trim(),
      subject: subjectMatch[1].trim(),
      content: contentMatch[1].trim()
    };
  } catch (error) {
    console.error('Error parsing email:', error);
    return null;
  }
};

export const parseMultipleEmails = (text: string): EmailData[] => {
  const emails: EmailData[] = [];
  
  // Split by numbered list and remove empty first element
  const emailBlocks = text.split(/\d+\./).slice(1);
  
  // Filter out the assistant's closing message
  const filteredBlocks = emailBlocks.filter(block => {
    // Skip blocks that contain common assistant closing phrases
    const closingPhrases = [
      'If you need more information',
      'If you need any further actions',
      'Let me know if you need',
      'Just let me know',
      'Is there anything else'
    ];
    return !closingPhrases.some(phrase => block.includes(phrase));
  });

  filteredBlocks.forEach(block => {
    const emailData = parseEmailFromText(block);
    if (emailData) {
      emails.push(emailData);
    }
  });

  return emails;
};

export const parseCalendarEventsFromText = (text: string): CalendarEvent[] => {
  try {
    const events: CalendarEvent[] = [];
    const eventBlocks = text.split(/\d+\./).slice(1); // Split by numbered list and remove empty first element

    eventBlocks.forEach(block => {
      const eventMatch = block.match(/\*\*Event\*\*: (.*?)(?=\s*-\s*\*\*Location\*\*:)/s);
      const locationMatch = block.match(/\*\*Location\*\*: (.*?)(?=\s*-\s*\*\*Time\*\*:)/s);
      const timeMatch = block.match(/\*\*Time\*\*: (.*?)$/s);

      if (eventMatch && locationMatch && timeMatch) {
        events.push({
          event: eventMatch[1].trim(),
          location: locationMatch[1].trim(),
          time: timeMatch[1].trim()
        });
      }
    });

    return events;
  } catch (error) {
    console.error('Error parsing calendar events:', error);
    return [];
  }
}; 