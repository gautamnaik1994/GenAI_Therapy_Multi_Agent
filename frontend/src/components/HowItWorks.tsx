import { therapyJson } from '../constants/therapyJson';
import AgentArch from '../assets/agents_graph.png';

function HowItWorks() {
  return (
    <div className='how-it-works card'>
      <h2>How this app works</h2>
      <ul>
        <li>
          <strong>Upload multiple therapy session files</strong>
          <div>
            You can upload a file containing multiple therapy session data. The
            file should be in JSON format and contain an array of session
            objects in following format:
            <pre>{JSON.stringify(therapyJson, null, 2)}</pre>
          </div>
        </li>
        <li>
          <strong>Data is processed by AI Agent </strong>
          <div>
            Below is the architecture of the AI agent that processes the therapy
            session data and generates insights:
            <div className='agent-arch'>
              <img src={AgentArch} alt='AI Agent Architecture' />
            </div>
            <ol>
              <li>
                The Supervisor Agent receives the therapy session data and tries
                to determine the diagnosis by keyword search.
              </li>
              <li>
                If the diagnosis is not clear, the agent will consult the LLM
                API for further insights.
              </li>
              <li>
                Depending on the diagnosis(anxiety or depression), the agent
                will route to the appropriate specialist agent.
              </li>
              <li>
                The specialist agent will analyze all the session data and
                generate a summary of the client's progress, which is displayed
                above in the frontend.
              </li>
            </ol>
          </div>
        </li>
        <li>
          <strong>Refer Github Readme for more details</strong>
          <div>
            You can find more details about the AI agent architecture and
            research behind this project in the{' '}
            <a
              href='https://github.com/gautamnaik1994/PsyTrackr?tab=readme-ov-file#agenticai-medical-assessment-project'
              target='_blank'
              rel='noopener noreferrer'
            >
              Github Readme
            </a>
            .
          </div>
        </li>
      </ul>
    </div>
  );
}
export default HowItWorks;
