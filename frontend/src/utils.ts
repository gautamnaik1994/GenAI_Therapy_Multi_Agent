export const response = {
  client_id: 'client3',
  sessions: [
    {
      therapy_session_number: 1,
      estimated_scores: {
        little_interest: 2,
        feeling_down: 2,
        trouble_sleeping: 2,
        feeling_tired: 2,
        poor_appetite: 2,
        feeling_bad_about_self: 2,
        trouble_concentrating: 1,
        slow_or_fast: 0,
        thoughts_of_self_harm: 1,
      },
      total_score: 14,
      justification:
        'The client reports persistent low mood, anhedonia, hypersomnia, low energy, decreased appetite, feelings of hopelessness, some difficulty concentrating, and passive thoughts of not wanting to wake up. These symptoms are present daily and are moderate in intensity, consistent with moderate depression.',
    },
    {
      therapy_session_number: 2,
      estimated_scores: {
        little_interest: 3,
        feeling_down: 3,
        trouble_sleeping: 2,
        feeling_tired: 3,
        poor_appetite: 2,
        feeling_bad_about_self: 3,
        trouble_concentrating: 2,
        slow_or_fast: 1,
        thoughts_of_self_harm: 1,
      },
      total_score: 20,
      justification:
        'Symptoms have worsened: profound sadness, anhedonia, hypersomnia, severe lack of motivation, decreased appetite, overwhelming emptiness, slowed cognition, and passive suicidal ideation. These are present all day, every day, and are severe, consistent with severe depression.',
    },
    {
      therapy_session_number: 3,
      estimated_scores: {
        little_interest: 1,
        feeling_down: 1,
        trouble_sleeping: 0,
        feeling_tired: 1,
        poor_appetite: 0,
        feeling_bad_about_self: 0,
        trouble_concentrating: 0,
        slow_or_fast: 0,
        thoughts_of_self_harm: 0,
      },
      total_score: 3,
      justification:
        'The client reports significant improvement: only mild low mood and anhedonia, normal sleep and appetite, improved energy, no self-worth or concentration issues, and no suicidal ideation. This is consistent with minimal depressive symptoms and partial remission.',
    },
  ],
  progress_summary:
    'The client initially presented with moderate depression (PHQ-9: 14), worsened to severe depression (PHQ-9: 20), and then showed substantial improvement to minimal symptoms (PHQ-9: 3). The overall trajectory is one of initial deterioration followed by significant recovery.',
  progress_status: 'Improving',
};
