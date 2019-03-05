import { JupyterLab, JupyterLabPlugin } from '@jupyterlab/application';
import { ServerConnection } from '@jupyterlab/services';
import {IMainMenu} from '@jupyterlab/mainmenu'
import {IFrame, ICommandPalette} from '@jupyterlab/apputils'
import {Menu} from '@phosphor/widgets'
import {URLExt} from '@jupyterlab/coreutils';
import '../style/index.css';

/**
 * Initialization data for the sotera_jupyter extension.
 */

const extension: JupyterLabPlugin<void> = {
  id: 'jupyter_wsgi',
  autoStart: true,
  requires: [IMainMenu, ICommandPalette],
  activate: activate_custom_menu
};

/**
   * Settings for making requests to the server.
   */
const SERVER_CONNECTION_SETTINGS = ServerConnection.makeSettings();

/**
  * The url endpoint for making requests to the server.
  */
const APPS_URL = URLExt.join(SERVER_CONNECTION_SETTINGS.baseUrl,'wsgi?json=True');

export function activate_custom_menu(app: JupyterLab, mainMenu: IMainMenu,
  palette: ICommandPalette): Promise<void> {

    function appendNewCommand(item: any)
    {
      let iframe : IFrame = null;
      let command = `wsgi-${item.name}:show`;
      console.log( `append command ${command}` );

      app.commands.addCommand(command, {
          label: item.name,
          execute: () =>
          {
            console.log( `Opening ${item.name}` );
            if ( iframe == null )
            {
                iframe = new IFrame();
                iframe.url = item.url;
                iframe.id = item.name;
                iframe.title.label = item.name;
                iframe.title.closable = true;
                iframe.node.style.overflowY = 'auto';
            }
            if (~iframe.isAttached )
            {
              app.shell.addToMainArea(iframe);
            }
            app.shell.activateById(iframe.id);
          }
        });
    }

    Private.getExtensionInfo().then( response => {
      if (response)
      {
        let menu = Private.createMenu(app, response);
        mainMenu.addMenu(menu, {rank: 80});
        for (let item of response.endpoints) {
            appendNewCommand(item);
        }
      }
    }
    )
    return Promise.resolve(void(0));
  }

namespace Private {

   export interface EndpointEntity {
     readonly url: string;
     readonly name: string;
     readonly mod: string;
   }

   export interface AppsInfo {
     readonly name: string;
     readonly endpoints?: (EndpointEntity)[] | null;
   }

  export async function getExtensionInfo() : Promise<AppsInfo>
  {
    const response = await ServerConnection.makeRequest( APPS_URL, {}, SERVER_CONNECTION_SETTINGS);
    if (response.status !== 200) {
        throw new ServerConnection.ResponseError(response);
    }
    return response.json();
  }

  export function createMenu(app: JupyterLab, extensionInfo: AppsInfo): Menu
  {
    const {commands} = app;
    let menu:Menu = new Menu({commands});
    menu.title.label = extensionInfo.name;
    for (let item of extensionInfo.endpoints ) {
      menu.addItem({command:`wsgi-${item.name}:show`})
    }
    return menu;
  }
}

export default extension;
